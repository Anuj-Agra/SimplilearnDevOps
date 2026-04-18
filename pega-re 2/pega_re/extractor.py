"""
extractor.py — Unpack JARs and catalog every file.
Deterministic. No LLM calls. Handles 200K+ rule files by writing to SQLite incrementally.
"""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree as ET

CATALOG_SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_files (
    path TEXT PRIMARY KEY,
    jar_source TEXT,
    size INTEGER,
    sha256 TEXT,
    obj_class_guess TEXT,
    ruleset_guess TEXT,
    is_rule INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_raw_obj_class ON raw_files(obj_class_guess);
CREATE INDEX IF NOT EXISTS idx_raw_ruleset ON raw_files(ruleset_guess);

CREATE TABLE IF NOT EXISTS warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage TEXT,
    severity TEXT,
    message TEXT
);
"""


@dataclass
class ExtractionResult:
    jars_found: int
    files_cataloged: int
    rule_files: int
    rulesets: list[str]
    warnings: list[str]


def extract_and_catalog(input_dir: str | Path, workdir: str | Path) -> ExtractionResult:
    input_dir = Path(input_dir)
    workdir = Path(workdir)
    unpacked = workdir / "unpacked"
    manifests = workdir / "manifests"
    unpacked.mkdir(parents=True, exist_ok=True)
    manifests.mkdir(parents=True, exist_ok=True)

    catalog = workdir / "catalog.sqlite"
    conn = sqlite3.connect(catalog)
    conn.executescript(CATALOG_SCHEMA)
    conn.commit()

    warnings: list[str] = []
    jars = list(input_dir.glob("*.jar"))
    already_unpacked = [p for p in input_dir.iterdir() if p.is_dir()]

    if not jars and not already_unpacked:
        raise FileNotFoundError(f"No .jar files or extracted jar directories in {input_dir}")

    # Unpack any JARs that aren't already unpacked
    for jar in jars:
        target = unpacked / jar.stem
        if target.exists():
            continue
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(jar) as zf:
            zf.extractall(target)

    # If the user already unpacked the JARs themselves, copy their tree in
    for d in already_unpacked:
        if d.name == "unpacked":
            continue
        dst = unpacked / d.name
        if not dst.exists():
            shutil.copytree(d, dst)

    rule_count = 0
    rulesets: set[str] = set()
    total = 0

    cur = conn.cursor()
    for jar_dir in unpacked.iterdir():
        if not jar_dir.is_dir():
            continue

        # Capture manifests
        for mf in jar_dir.rglob("pega.xml"):
            shutil.copy2(mf, manifests / f"{jar_dir.name}__pega.xml")
        for mf in jar_dir.rglob("MANIFEST.MF"):
            shutil.copy2(mf, manifests / f"{jar_dir.name}__MANIFEST.MF")

        for f in jar_dir.rglob("*"):
            if not f.is_file():
                continue
            total += 1
            size = f.stat().st_size
            is_rule = f.suffix.lower() in {".xml", ".pegarules"}
            obj_class = ruleset = None

            if is_rule and size < 5 * 1024 * 1024:  # skip >5 MB files from quick-peek
                obj_class, ruleset = _peek_rule_root(f)
                if obj_class:
                    rule_count += 1
                if ruleset:
                    rulesets.add(ruleset)

            sha = _sha256_of(f) if size < 2 * 1024 * 1024 else ""
            cur.execute(
                "INSERT OR REPLACE INTO raw_files "
                "(path, jar_source, size, sha256, obj_class_guess, ruleset_guess, is_rule) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(f.relative_to(unpacked)), jar_dir.name, size, sha, obj_class, ruleset, int(is_rule and obj_class is not None)),
            )

            if total % 10_000 == 0:
                conn.commit()

    conn.commit()

    # Scale sanity check
    if rule_count < 50_000:
        warnings.append(f"scale_warning: only {rule_count} rule files detected — verify all jars unpacked")
    if rule_count > 500_000:
        warnings.append(f"scale_warning: {rule_count} rule files — unusually large, verify no duplication")

    for w in warnings:
        cur.execute("INSERT INTO warnings (stage, severity, message) VALUES (?, ?, ?)", ("extractor", "warn", w))
    conn.commit()
    conn.close()

    return ExtractionResult(
        jars_found=len(jars) or len(already_unpacked),
        files_cataloged=total,
        rule_files=rule_count,
        rulesets=sorted(rulesets),
        warnings=warnings,
    )


def _peek_rule_root(path: Path) -> tuple[str | None, str | None]:
    """Read just the root element's attributes. Streaming, fast."""
    try:
        # iterparse with only 'start' events so we can bail after the root
        context = ET.iterparse(path, events=("start",))
        for _, elem in context:
            obj_class = elem.attrib.get("pxObjClass") or elem.attrib.get("pyObjClass")
            ruleset = elem.attrib.get("pyRuleSet") or elem.attrib.get("pxRuleSet")
            return obj_class, ruleset
    except ET.ParseError:
        return None, None
    return None, None


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_rule_files(catalog_path: str | Path, unpacked_dir: str | Path) -> Iterator[tuple[Path, str | None]]:
    """Yield (abs_path, obj_class_guess) for every rule file in the catalog."""
    conn = sqlite3.connect(catalog_path)
    cur = conn.execute("SELECT path, obj_class_guess FROM raw_files WHERE is_rule = 1")
    unpacked_dir = Path(unpacked_dir)
    for rel, obj in cur:
        yield unpacked_dir / rel, obj
    conn.close()

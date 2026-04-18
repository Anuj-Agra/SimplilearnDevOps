---
name: pega-extractor
description: Use whenever the task starts from Pega JAR/PegaRules archive exports that need to be unpacked and inventoried before any rule analysis. Produces a file-level catalog of every rule XML and binary asset, without parsing rule content.
---

# Skill: Pega Extractor

## Purpose
Turn a folder of Pega JAR exports (or already-extracted JAR contents) into a deterministic **file catalog** that later agents can stream from. No rule interpretation happens here.

## Inputs
- `input_dir` — path containing either `.jar` files or already-unpacked JAR contents
- `workdir` — writable directory for the catalog and any unpacked files

## Outputs
- `workdir/unpacked/` — extracted contents of every JAR (deduplicated by SHA-256)
- `workdir/catalog.sqlite` — with table `raw_files(path, jar_source, size, sha256, obj_class_guess, ruleset_guess)`
- `workdir/manifests/*.xml` — one copy of each `pega.xml` / `MANIFEST.MF` found

## Instructions (for the LLM driving this step)

1. Call `pega_re.extractor.extract_and_catalog(input_dir, workdir)`. Do **not** try to parse rule XML yourself — that is the RuleParser's job.
2. Verify every JAR had at least one `META-INF/pega.xml`. If any JAR is missing one, flag it in the `warnings` list on the state object but continue.
3. From `pega.xml` read the `<Ruleset>` and version declarations; these become the `ruleset_guess` column. This is a *guess* because rules can override their ruleset in the rule XML itself — the parser agent will reconcile.
4. When this step finishes, emit one line per JAR summarising: jar name, ruleset(s) declared, rule file count, binary asset count.
5. If the total rule count is below 50,000 or above 500,000, emit a `scale_warning` — a normal Pega app sits in the 10K–300K range.

## Non-goals
- Do not parse any rule XML beyond reading the root `pxObjClass` attribute.
- Do not load rule content into memory.
- Do not attempt to deduplicate *rules* (same-name rules in different rulesets are intentional overrides).

## Example invocation (Claude / Copilot)
> "Extract the four jars in `./pega_jars/` into `./workdir/` using the pega-extractor skill, then report per-jar ruleset summary."

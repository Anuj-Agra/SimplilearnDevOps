# Python Mono Repo Parser

## Detect Package Structure

```bash
# Find all pyproject.toml, setup.py, setup.cfg
find <repo_root> -name "pyproject.toml" -o -name "setup.py" -o -name "setup.cfg" \
  | grep -v "/.venv/" | grep -v "/dist/" | sort

# Find all requirements.txt (flat repos)
find <repo_root> -name "requirements*.txt" \
  | grep -v "/.venv/" | sort
```

## Extract Package Names

### pyproject.toml (PEP 517/518)
```toml
[project]
name = "my-service-a"
version = "0.1.0"
dependencies = [
  "my-shared-lib>=1.0",           # internal dep
  "requests>=2.28",               # external — skip
]
```

### setup.py / setup.cfg
```python
setup(
    name="my-service-a",
    install_requires=[
        "my-shared-lib",          # internal dep
        "flask",                   # external — skip
    ],
)
```

## Internal vs External Dependencies

A dependency is **internal** if its name matches another package defined in the same repo.
Build a set of all internal package names first, then filter:

```bash
# Collect all internal package names
grep -rn "^name = " <repo_root> --include="pyproject.toml" \
  | sed 's/.*name = "//' | sed 's/"//' | sort > /tmp/internal_packages.txt

grep -rn "name=" <repo_root> --include="setup.py" \
  | grep -v "file_name\|display_name\|full_name" \
  | sed "s/.*name=['\"]//;s/['\"].*//" | sort >> /tmp/internal_packages.txt
```

## Python Import Analysis (code-level)

```bash
# Find imports from sibling packages (relative or by name)
grep -rn "^from \.\|^import \." <repo_root> --include="*.py" \
  | grep -v "/.venv/" | grep -v "/dist/"

# Find cross-package imports by name
# For each internal package name, grep for imports of it
while read pkg; do
  echo "=== $pkg ==="
  grep -rn "import $pkg\|from $pkg" <repo_root> --include="*.py" \
    | grep -v "/.venv/" | grep -v "/dist/" | head -10
done < /tmp/internal_packages.txt
```

## Namespace Packages

If using namespace packages (no `__init__.py`), infer boundaries from directory structure:
```bash
# Top-level Python namespace roots
find <repo_root> -maxdepth 3 -name "__init__.py" \
  | grep -v "/.venv/" | sort
```

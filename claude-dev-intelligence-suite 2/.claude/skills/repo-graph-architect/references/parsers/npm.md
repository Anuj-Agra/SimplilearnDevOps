# npm / yarn / pnpm Workspace Parser

## Detect Workspace Config

```bash
# npm / yarn (root package.json)
cat <repo_root>/package.json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print(d.get('workspaces','NONE'))"

# pnpm (pnpm-workspace.yaml)
cat <repo_root>/pnpm-workspace.yaml
```

## Find All Packages

```bash
# All package.json files (exclude node_modules)
find <repo_root> -name "package.json" \
  | grep -v "node_modules" \
  | grep -v "/.cache/" \
  | sort
```

## Extract Package Identity

For each `package.json`:
```json
{
  "name": "@myorg/service-a",        // node id — use full scoped name
  "version": "1.2.0",
  "private": true                    // private=true = internal package
}
```

Use `name` as node `id`. Strip `@myorg/` for the display `label`.

## Detect Hierarchy from Path

Map the file path to hierarchy:
- `packages/service-a/package.json` → parent = `packages`, label = `service-a`
- `apps/web/package.json` → parent = `apps`, label = `web`
- `libs/shared/utils/package.json` → parent = `libs:shared`, label = `utils`

## Extract Internal Dependencies

```json
{
  "dependencies": {
    "@myorg/shared-lib": "workspace:*",    // internal
    "@myorg/common-utils": "^1.0.0",       // may be internal
    "lodash": "^4.17.21"                   // external — skip
  },
  "devDependencies": {
    "@myorg/test-utils": "workspace:*"     // internal test dep
  },
  "peerDependencies": {
    "@myorg/core": "*"                     // peer dep
  }
}
```

Internal package indicators:
- Value = `"workspace:*"` or `"workspace:^"` (pnpm/yarn v2+)
- Name starts with the org's scope (`@myorg/`)
- Version matches another package's exact version in the repo

## Grep Approach

```bash
# Find all workspace: references (pnpm/yarn berry)
grep -rn '"workspace:' <repo_root> \
  --include="package.json" | grep -v "node_modules"

# Find all @myorg/ internal references
grep -rn '"@<YOUR_ORG>/' <repo_root> \
  --include="package.json" | grep -v "node_modules"
```

## TypeScript / Angular Path Aliases (tsconfig.json)

These reveal implicit module boundaries:

```bash
# Extract path aliases = module boundaries
grep -rn '"paths"' <repo_root> \
  --include="tsconfig*.json" | grep -v "node_modules"

cat <repo_root>/tsconfig.json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); \
   paths=d.get('compilerOptions',{}).get('paths',{}); \
   [print(k,'->',v) for k,v in paths.items()]"
```

## Lerna Support

```bash
cat <repo_root>/lerna.json
# packages field lists globs for package locations
```

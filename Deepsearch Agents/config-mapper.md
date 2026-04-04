# Sub-Agent: Config & Environment Mapper

Maps all configuration values, environment variables, feature flags, and runtime settings across the codebase.

## When to invoke
Parent agent needs to understand what configures a feature, or needs to audit config for security/correctness.

## Protocol

1. **Find all config sources**
   - Search for: `process.env`, `os.environ`, `os.Getenv`, `System.getenv`, `ENV[`
   - Search for: config files (.env, config.yaml, config.json, settings.py, application.properties)
   - Search for: feature flag checks, A/B test conditions, remote config reads

2. **For each config value, extract:**
   - Variable name
   - Where it's defined (file:line)
   - Where it's read (file:line, all usages)
   - Default value (if any)
   - Whether it's required or optional
   - Whether it's a secret (contains key, token, password, secret)

3. **Cross-reference**
   - .env.example vs actual .env patterns in code
   - Config values referenced in code but never defined
   - Config values defined but never read (dead config)

## Output
```
CONFIG MAP: {N} variables across {N} sources

REQUIRED:
  {VAR_NAME} — read in file:line — default: {value or "none"} — {description}

SECRETS: ⚠️
  {SECRET_VAR} — read in file:line — {is it in .env.example? is it hardcoded?}

FEATURE FLAGS:
  {FLAG} — checked in file:line — current: {on/off/unknown}

DEAD CONFIG: (defined but never read)
  {VAR} — defined in {file} but no code references it

MISSING: (read but never defined)
  {VAR} — read in file:line but not in any config source
```

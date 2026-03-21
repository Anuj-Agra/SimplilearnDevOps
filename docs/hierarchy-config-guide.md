# Hierarchy Config Guide

How to configure and run the analysis engine against a real PEGA export — 4 folders of
`.bin` files with manifest `.json` files, organised as:

```
COB → CRDFWApp → MSFWApp → PegaRules
```

---

## Folder structure

Your PEGA export should look like this:

```
pega-export/
├── COB/
│   ├── COBRules-01-02-01.json          ← manifest (rule inventory)
│   ├── COBRules-01-01-05.json          ← older manifest version
│   ├── KYC_CDDOnboarding.bin           ← native PEGA rule binary
│   ├── KYC_RiskScoring.bin
│   └── ... (many .bin files)
│
├── CRDFWApp/
│   ├── CRDFWApp-01-05-03.json          ← manifest
│   ├── *.bin
│   └── ...
│
├── MSFWApp/
│   ├── MSFWApp-01-04-00.json
│   ├── *.bin
│   └── ...
│
└── PegaRules/
    ├── PegaRules-08-07-01.json
    ├── *.bin
    └── ...
```

Key points:
- Each folder can have **multiple manifest JSON files** — the engine picks the right one based on your config.
- `.bin` files are the native PEGA rule content. The engine extracts strings and cross-references from them; it does not need a Java runtime.
- Folder names can differ from the examples above — what matters is the path you set in `config/analysis_config.yaml`.

---

## Step 1 — Edit analysis_config.yaml

Open `config/analysis_config.yaml` and update the `hierarchy` section:

```yaml
hierarchy:

  - name: COB
    tier: 0
    folder: ./pega-export/COB        # ← change this to your actual path
    manifest_version: latest          # ← or "01-02-01" for a specific version
    include_in_analysis: true         # ← true = rules queued for LLM analysis

  - name: CRDFWApp
    tier: 1
    folder: ./pega-export/CRDFWApp
    manifest_version: latest
    include_in_analysis: true

  - name: MSFWApp
    tier: 2
    folder: ./pega-export/MSFWApp
    manifest_version: latest
    include_in_analysis: false        # ← false = loaded as context only, no LLM cost

  - name: PegaRules
    tier: 3
    folder: ./pega-export/PegaRules
    manifest_version: latest
    include_in_analysis: false
```

And update the analysis section:

```yaml
analysis:
  root_casetype: KYC-Work-CDD         # ← pyRuleName of your root Case Type
  role: ba                             # ← ba | po | dev | qa
  max_rules_per_session: 50
  token_budget_per_rule: 6000

workspace: ./workspaces/kyc-cdd-analysis
```

---

## Step 2 — Find your root_casetype name

The `root_casetype` value is the `pyRuleName` of the Case Type at the top of your KYC
workflow. To find it:

1. Open any manifest JSON in a text editor
2. Search for `"pxObjClass": "Rule-Obj-CaseType"` in the `pxResults` array
3. The `pyRuleName` field on that entry is your value

Example:
```json
{
  "pyRuleName": "KYC-Work-CDD",
  "pyClassName": "KYC-Work-CDD",
  "pxObjClass": "Rule-Obj-CaseType",
  ...
}
```
→ Set `root_casetype: KYC-Work-CDD`

---

## Step 3 — Choose manifest versions

### Using "latest" (recommended for most teams)

```yaml
manifest_version: latest
```

The engine scans your folder for JSON files that contain PEGA rule inventory data,
reads the `pyRuleSetVersion` field from each, and picks the one with the highest version.
No manual tracking of version numbers required.

### Using an exact version

```yaml
manifest_version: "01-02-03"
```

The engine looks for a manifest whose `pyRuleSetVersion` field (or filename) matches
`01-02-03`. Both dot and dash separators are accepted (`01.02.03` works too).

**When to use exact versions:**
- You have multiple manifests and want to pin to a specific release
- Your team standardises on a known-good version for analysis
- You want reproducible results regardless of what new manifests appear in the folder

### Checking what was resolved before running analysis

```bash
python tools/run.py validate-config --config config/analysis_config.yaml
```

Output:
```
================================================================
  Config validation report
================================================================
  Config file    : /path/to/config/analysis_config.yaml
  Workspace      : ./workspaces/kyc-cdd-analysis
  Root CaseType  : KYC-Work-CDD
  Role           : ba
  Model          : claude-sonnet-4-20250514
  Max rules/sess : 50
  Token budget   : 6000

  Application hierarchy:
  Tier   Name           Folder   BINs  Manifests  Selected manifest               Analyse?
  -----------------------------------------------------------------------
  [0]    COB            ✓          87          2  COBRules-01-02-01.json          True
  [1]    CRDFWApp       ✓         203          1  CRDFWApp-01-05-03.json          True
  [2]    MSFWApp        ✓         412          3  MSFWApp-01-04-00.json           False
  [3]    PegaRules      ✓        1240          1  PegaRules-08-07-01.json         False

  ✓ All folders and manifests resolved — ready to run
```

If any row shows `✗ MISSING` or `✗ NOT FOUND`, fix the path or manifest before proceeding.

---

## Step 4 — Build the rule graph (free — no LLM calls)

```bash
python tools/run.py graph --config config/analysis_config.yaml
```

This prints:
- **Rule graph statistics** — total nodes, how many have BIN files, cycle count
- **Analysis queue** — the 50+ rules that will be analysed, in dependency order
- **Context-only nodes** — rules from MSFWApp/PegaRules loaded but not queued
- **Unresolved references** — rules referenced but not found in any manifest

Review the queue before spending any API budget. A healthy first-run typically shows:
- 0 cycles
- 10–30% of references unresolved (normal — some rules live in other apps)
- Analysis queue starts with Rule-Obj-CaseType at depth=0

---

## Step 5 — Run the analysis

```bash
python tools/run.py analyse --config config/analysis_config.yaml
```

The engine:
1. Loads the most-specific version of each rule (COB overrides CRDFWApp, etc.)
2. Extracts cross-rule references from `.bin` files
3. Analyses each rule via the Anthropic API in BFS order (root CaseType first)
4. Saves each output to `workspaces/kyc-cdd-analysis/analysis/`
5. Checkpoints after every rule — safe to stop and re-run

**Session limits:**

By default, 50 rules are processed per run. For a codebase with 200 analysable rules,
you will need 4 sessions. Re-run the same command each time:

```bash
# Session 1 — rules 1-50
python tools/run.py analyse --config config/analysis_config.yaml

# Session 2 — rules 51-100 (auto-resumes from checkpoint)
python tools/run.py analyse --config config/analysis_config.yaml

# ... repeat until "Analysis complete"
```

Check progress between sessions:
```bash
python tools/run.py status --workspace ./workspaces/kyc-cdd-analysis
```

---

## Step 6 — Aggregate outputs

Once all (or enough) rules are analysed:

```bash
python tools/run.py aggregate --config config/analysis_config.yaml
```

Or equivalently:
```bash
python tools/run.py aggregate --workspace ./workspaces/kyc-cdd-analysis
```

Produces in `workspaces/kyc-cdd-analysis/aggregated/`:

| File | Contents | Feed into |
|------|----------|-----------|
| `full_flow_narrative.md` | Every rule analysed in depth order — plain-English codebase description | Agent 02 (BRD Writer) |
| `frd_fragments.md` | FRD FR blocks for each Flow rule | Agent 03 (FRD Writer) |

---

## Understanding most-specific-wins

When the same rule (`pyClassName::pyRuleName`) exists in multiple tiers:

```
Example: "KYC_RiskScoring" in class "KYC-Work-CDD"

  COB       tier 0  →  WINS — this version is used for analysis
  CRDFWApp  tier 1  →  discarded (overridden by COB)
  MSFWApp   tier 2  →  discarded (overridden by COB)
  PegaRules tier 3  →  discarded (overridden by COB)
```

This mirrors how PEGA resolves rules at runtime — the most application-specific rule
takes precedence over framework defaults.

**Important:** "same rule" means exact match on both `pyClassName` AND `pyRuleName`.
A rule named `KYC_RiskScoring` in class `COB-Work-CDD` and the same rule name in class
`CRDFWApp-Work-CDD` are treated as **different rules** and both are retained.

---

## Tuning include_in_analysis

| Setting | Effect | Use when |
|---------|--------|---------|
| `include_in_analysis: true` | Rules from this app are queued for LLM analysis | The app contains your client-specific KYC logic |
| `include_in_analysis: false` | Rules are in the graph as context nodes only — no LLM calls | Framework/base rules you want available for dependency resolution but don't need individually narrated |

**Cost impact:** Setting MSFWApp and PegaRules to `false` can reduce your LLM call count
by 70–80% while still making those rules available as context when analysing COB flows.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `✗ MISSING` folder in validate-config | Path in config doesn't exist | Check for typos; use absolute path if relative isn't resolving |
| `✗ NOT FOUND` manifest | No JSON files in folder look like manifests | Check that the manifest files contain `pxResults` or similar PEGA export keys |
| `manifest_version: "01-02-03"` not resolved | Version string doesn't match `pyRuleSetVersion` in any file | Run validate-config, check exact version strings; try `latest` |
| 0 rules loaded from an app | Manifest exists but all rules are Blocked/Withdrawn, or rule_type_filter excludes them all | Check rule_type_filter settings; check pyAvailability values in manifest |
| Analysis queue is smaller than expected | MSFWApp/PegaRules rules correctly excluded | Expected — only `include_in_analysis: true` apps are queued |
| BIN extraction produces no references | BIN files use a non-standard serialisation format | Check `bin_extraction.min_string_length` — try lowering to 3 |
| Root CaseType not found | `root_casetype` value doesn't match any manifest entry | Check exact `pyRuleName` in the manifest; it's case-sensitive |

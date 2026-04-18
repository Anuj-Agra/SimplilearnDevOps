# Cluster Analyzer

Agent-based health, capacity, and efficiency analyzer for **Redis** + **Elasticsearch** clusters used in high-availability data distribution setups.

Six narrow-focus agents inspect a live snapshot of each cluster, emit ranked findings with concrete recommendations, and surface them through a CLI and a Streamlit dashboard.

---

## Why this design

- **Collection is deterministic Python** against live clusters. Agents only reason over the collected snapshot — they never hit the cluster themselves. This keeps agents fast, unit-testable with fixtures, and free of hallucinated metrics.
- **Six narrow agents** beat one mega-agent. Each has a single remit, is easy to reason about, and is easy to extend or swap.
- **Ranking by impact × severity**, so the top of the list is what to fix first — not a wall of equally-weighted warnings.
- **Failure-tolerant**: if one probe or agent throws, the rest of the run still completes and the error is captured in the report.

---

## What it checks

| Agent | Remit |
|---|---|
| **CapacityAnalyst** | Redis memory vs maxmemory, evictions, fragmentation; ES JVM heap, disk watermarks, oversized shards |
| **LatencyProfiler** | Redis slowlog + `LATENCY LATEST`, client count; ES thread-pool rejections, tripped circuit breakers, pending master tasks |
| **TopologyAuditor** | Redis replica count + lag, cluster node states; ES cluster status, master-eligible count (even/odd, split-brain), shard distribution skew |
| **ConfigLinter** | Live `CONFIG GET` and ES cluster settings compared against a YAML baseline; always-on checks for auth posture and persistence |
| **WorkloadProfiler** | Big keys (via `SCAN` + `MEMORY USAGE`), key-type distribution; ES shards-per-GB-heap ratio, mapping field explosion, tiny-index sprawl |
| **ResilienceValidator** | Redis RDB/AOF recency and rewrite status; ES ILM presence, unassigned shards |

---

## Install

```bash
git clone <this repo>
cd cluster_analyzer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.10+ required.

---

## Run

### CLI

```bash
python run_cli.py \
    --redis-host redis-primary.internal --redis-port 6379 \
    --es-host https://es-01.internal:9200 \
    --es-host https://es-02.internal:9200 \
    --baseline config/baseline.yaml \
    --out report.json
```

Credentials can also come from environment variables: `REDIS_PASSWORD`, `ES_PASSWORD`, `ES_API_KEY`.

For a Redis Cluster instead of standalone/sentinel: add `--redis-cluster`.

### Streamlit dashboard

```bash
streamlit run app.py
```

Enter connection details in the sidebar, click **Run analysis**. The dashboard shows KPIs, severity/area breakdowns, filterable findings with per-finding evidence, and a JSON export.

### Analyze only one system

Either `--redis-host` or `--es-host` can be omitted. The orchestrator skips missing collectors and still runs all agents against whatever snapshot is available.

---

## Project layout

```
cluster_analyzer/
├── run_cli.py                      # CLI entry point
├── app.py                          # Streamlit dashboard
├── requirements.txt
├── config/
│   └── baseline.yaml               # ConfigLinter policy rules
└── cluster_analyzer/
    ├── __init__.py
    ├── models.py                   # Finding, Severity, Area, ReportBundle
    ├── base_agent.py               # BaseAgent ABC
    ├── orchestrator.py             # collect + run agents + rank
    ├── collectors/
    │   ├── redis_collector.py      # INFO, CONFIG, SLOWLOG, LATENCY, SCAN sample, cluster topology
    │   └── elastic_collector.py    # cluster health, nodes_stats, cat APIs, settings, ILM
    └── agents/
        ├── capacity_analyst.py
        ├── latency_profiler.py
        ├── topology_auditor.py
        ├── config_linter.py
        ├── workload_profiler.py
        └── resilience_validator.py
```

---

## The baseline file

`config/baseline.yaml` drives the `ConfigLinter`. Rules support `allowed`, `equals`, `min`, `max`, plus per-rule `severity`, `rationale`, and `fix`:

```yaml
redis:
  maxmemory-policy:
    allowed: [allkeys-lru, allkeys-lfu, volatile-lru, volatile-lfu, noeviction]
    severity: HIGH
    rationale: "Eviction policy must match workload."

elasticsearch_cluster:
  action.destructive_requires_name:
    equals: "true"
    severity: MEDIUM
```

Edit this file — no code changes needed — to match your SRE and security standards (e.g., tighten `maxmemory-policy` to only `allkeys-lru` for your cache tier, forbid `save ""` on persistent Redis, require disk watermarks enabled on ES).

---

## Report shape

Every run produces a `ReportBundle` that serializes to JSON:

```json
{
  "generated_at": "2026-04-17T09:30:00+00:00",
  "redis_snapshot":   { ... raw snapshot ... },
  "elastic_snapshot": { ... raw snapshot ... },
  "findings": [
    {
      "agent": "CapacityAnalyst",
      "system": "redis",
      "area": "capacity",
      "severity": "HIGH",
      "score": 60,
      "title": "Redis memory at 87% of maxmemory",
      "detail": "used_memory=... maxmemory=...",
      "recommendation": "Scale up, shard, or shed load...",
      "evidence": { "used_memory": ..., "maxmemory": ..., "ratio": 0.87 }
    }
  ],
  "errors": []
}
```

Findings are sorted highest-impact first. The `evidence` block is what you'd attach to a ticket or use as context when asking an LLM to draft remediation steps.

---

## Extending

**Add a new rule to the linter** — edit `config/baseline.yaml`, no code change.

**Add a new agent** — subclass `BaseAgent`, implement `analyze(redis_snapshot, elastic_snapshot) -> list[Finding]`, register it in `cluster_analyzer/agents/__init__.py` and in `orchestrator.run_analysis`.

**Add a new probe** — extend `RedisCollector` or `ElasticCollector`. Keep probes wrapped in try/except so one failing API doesn't kill the whole snapshot.

**Plug into an LLM for synthesis** — pass `summarize(bundle)` into a prompt to generate an executive-friendly remediation plan. The data layer is fully deterministic, so the LLM is doing writing, not measuring.

---

## Operational notes

- **Keyspace sampling uses `SCAN`**, never `KEYS *`. Sample size is capped (default 2,000 keys) and tunable via `RedisConnectionConfig.sample_size`. Safe to run against production.
- **Elasticsearch probes are read-only**: cluster/node/indices stats, cat APIs, and settings. No mutations.
- **Run on a read-only user**. Redis: create an ACL user with `+@read +@connection +cluster|info +memory +slowlog +latency +config|get +scan +type`. ES: a role with `monitor` cluster privilege and `view_index_metadata` over the indices you want inspected is enough.
- **Runtime**: a full run against a mid-size cluster (10 ES nodes, 50 indices, Redis with 2,000-key sample) typically completes in 5–15 seconds.

---

## Limitations / roadmap

- No time-series. Current snapshot only. Pair with Prometheus exporters (`redis_exporter`, `elasticsearch_exporter`) + Grafana for trending.
- ES snapshot repository recency isn't checked (collector doesn't call the snapshot API). Add a probe if you need RTO/RPO posture validation.
- No automated remediation — by design. All findings are advisory with recommended actions.
- Redis Sentinel topology is not inspected directly; Sentinel-specific checks are a natural next agent.

# structural_observability

Unified Python package for:

- **CP-SAT tearing classification** (`C_cl`, `C_ext`, `C_dir`)
- **PDF-style minimum instrumentation repair** (combinatorial search)
- Future **Streamlit UI** (Phase 3)

Version **0.3.0** -- Phase 3 Streamlit UI (simple PT labels).

## Paper engine (standby)

The code cited in the paper remains at
[romulobrito/cp-sat-tearing](https://github.com/romulobrito/cp-sat-tearing)
(`cp-sat-tearing-public/` locally). That repository is **frozen for the paper**.
Active development is **only** in this package.

## Install

```bash
cd structural_observability
pip install -e ".[app]"
```

## Quick start

```bash
# Semantics tests
python tests/test_tearing_semantics.py
python tests/test_urs_pdf_regression.py

# YAML-driven case (classify or min_repair)
structural-obs-run --case cases/urs_pdf_real.yaml

# Streamlit UI (simple Portuguese)
structural-obs-app
```

## Package layout

```text
src/structural_obs/
  tearing/          # classification engine + benchmark registry
  toolkit/          # schemas, min repair, classify service, CLI
  app/              # Streamlit UI (simple PT labels)
cases/              # YAML case definitions (schema v1.0)
tests/
```

## CLI commands

| Command | Description |
|---------|-------------|
| `structural-obs-run` | Run a YAML case (classify or min_repair) |
| `structural-obs-app` | Streamlit UI (diagnostico + instrumentacao minima) |
| `structural-obs-run-cases` | Run registered tearing benchmark cases |
| `structural-obs-min-inst` | PDF minimum instrumentation analysis |
| `structural-obs-ablation` | Matching preprocessing ablation |
| `structural-obs-benchmark` | Timing benchmark (Narasimhan) |
| `structural-obs-campaign` | Additive classification and minimum instrumentation |

Outputs: `results/` (gitignored).

## Additive injection-system campaign

The complete injection-system campaign keeps the paper classification engine
unchanged. It normalizes declared duplicates, partitions independent incidence
components, classifies every cumulative block, expands automatic candidate
tiers, solves the minimum-instrumentation CP-SAT model, and audits the selected
sensors with the frozen classifier.

```bash
# Classification only
structural-obs-campaign \
  --campaign cases/injection_system_additive.yaml \
  --mode classify

# Generate a reviewable candidate list without optimization
structural-obs-campaign \
  --campaign cases/injection_system_additive.yaml \
  --mode generate-candidates

# Optimize with automatic candidates (the reviewed mode remains supported)
structural-obs-campaign \
  --campaign cases/injection_system_additive.yaml \
  --mode optimize

# Resume certified stages from a previous run
structural-obs-campaign \
  --campaign cases/injection_system_additive.yaml \
  --mode optimize \
  --resume-from results/campaigns/injection_system_additive/run_TIMESTAMP
```

The campaign YAML may set `solver.num_search_workers`. This case uses 4
workers. The paper engine default remains 1 worker.

`cases/injection_system_additive.yaml` targets the active variables listed by
`variaveis_calculadas`. `cases/injection_system_full_observability.yaml` uses
the same blocks and input measurements, but each stage targets every active
variable. A minimum is certified only when the primary
sensor-cost phase returns `OPTIMAL` in every target component and frozen-core
validation closes every target. Adaptive retries, component certificates, and
SHA-256 resume fingerprints are saved in JSON and XLSX. The `reviewed`
candidate mode and optional approved/prohibited lists can be enabled in the
campaign YAML when engineering intervention is required.

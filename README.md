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

Outputs: `results/` (gitignored).

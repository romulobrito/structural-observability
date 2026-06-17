# structural_observability

Unified Python package for:

- **CP-SAT tearing classification** (`C_cl`, `C_ext`, `C_dir`)
- **PDF-style minimum instrumentation repair** (combinatorial search)
- Future **Streamlit UI** (Phase 3)

Version **0.2.0** -- Phase 2 YAML cases and unified CLI.

## Paper engine (standby)

The code cited in the paper remains at
[romulobrito/cp-sat-tearing](https://github.com/romulobrito/cp-sat-tearing)
(`cp-sat-tearing-public/` locally). That repository is **frozen for the paper**.
Active development is **only** in this package. See [MIGRATION.md](MIGRATION.md).

## Install

```bash
cd structural_observability
pip install -e .
```

## Quick start

```bash
# Semantics tests
python tests/test_tearing_semantics.py
python tests/test_urs_pdf_regression.py

# YAML-driven case (classify or min_repair)
structural-obs-run --case cases/urs_pdf_real.yaml
structural-obs-run --case cases/urs_pdf_repair.yaml --objective min_repair

# Paper benchmark cases (subset)
structural-obs-run-cases --case 01_urs_ideal --case 02_urs_real --case 10_urs_real_RaC_RaD

# PDF minimum instrumentation (Sec. 4.1-4.2.3)
structural-obs-min-inst
```

## Package layout

```text
src/structural_obs/
  tearing/          # classification engine + benchmark registry
  toolkit/          # schemas, min repair, classify service, CLI
cases/              # YAML case definitions (schema v1.0)
tests/
```

## Documentation

See [MIGRATION.md](MIGRATION.md) for package layout and legacy folder mapping.

## CLI commands

| Command | Description |
|---------|-------------|
| `structural-obs-run` | Run a YAML case (classify or min_repair) |
| `structural-obs-run-cases` | Run registered tearing benchmark cases |
| `structural-obs-min-inst` | PDF minimum instrumentation analysis |
| `structural-obs-ablation` | Matching preprocessing ablation |
| `structural-obs-benchmark` | Timing benchmark (Narasimhan) |

Outputs: `results/` (gitignored).

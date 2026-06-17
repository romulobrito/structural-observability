# Migration notes

## Canonical development location

Active development lives in **`structural_observability/`** (this package).

## Standby sources (do not edit for new features)

| Path | Role | Paper link |
|------|------|------------|
| `../cp-sat-tearing-public/` | Frozen paper reproduction snapshot | https://github.com/romulobrito/cp-sat-tearing |
| `../urs_pdf_min_instrumentation/` | Prototype absorbed into `toolkit/` | superseded |

The tearing engine code was **migrated once** from `cp-sat-tearing-public/src/`
into `src/structural_obs/tearing/`. Future changes happen **only here**.

## Mapping

| Old location | New location |
|--------------|--------------|
| `cp-sat-tearing-public/src/cpsat_tearing_core_impl.py` | `src/structural_obs/tearing/core.py` |
| `cp-sat-tearing-public/src/case_registry_impl.py` | `src/structural_obs/tearing/registry.py` |
| `cp-sat-tearing-public/src/*_case.py` | `src/structural_obs/tearing/cases/` |
| `cp-sat-tearing-public/scripts/run_cases.py` | `src/structural_obs/tearing/cli/run_cases.py` |
| `urs_pdf_min_instrumentation/min_inst_search.py` | `src/structural_obs/toolkit/services/min_repair.py` |
| `urs_pdf_min_instrumentation/pdf_premises.py` | `src/structural_obs/toolkit/premises.py` |
| `urs_pdf_min_instrumentation/run_min_instrumentation.py` | `src/structural_obs/toolkit/cli/min_instrumentation.py` |

## Install and run

```bash
cd structural_observability
pip install -e .
python tests/test_tearing_semantics.py
python tests/test_urs_pdf_regression.py
structural-obs-run-cases --case 01_urs_ideal --case 02_urs_real
structural-obs-min-inst --mode repair
```

## Versioning

- Package version: `pyproject.toml` (`0.1.0` at migration).
- Paper reproduction: continue citing `romulobrito/cp-sat-tearing` tag frozen for the article.
- New features and UI: cite this repository and its tags.

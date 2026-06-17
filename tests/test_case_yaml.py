#!/usr/bin/env python3
"""Round-trip tests: YAML cases -> expected metrics."""

from __future__ import annotations

from pathlib import Path

from structural_obs import PROJECT_ROOT
from structural_obs.toolkit.schemas.loaders import load_case, save_case
from structural_obs.toolkit.services.classify_service import run_case

CASES_DIR = PROJECT_ROOT / "cases"


def test_load_urs_ideal_has_19_equations() -> None:
    case = load_case(CASES_DIR / "urs_pdf_ideal.yaml")
    assert case.equations_profile == "urs_document"
    assert len(case.equations) == 19
    assert len(case.all_variables) == 43


def test_classify_ideal_full_coverage() -> None:
    case = load_case(CASES_DIR / "urs_pdf_ideal.yaml")
    run = run_case(case)
    assert run.classification is not None
    assert run.classification.c_closed == 43
    assert run.classification.criterion_satisfied


def test_classify_real_partial_coverage() -> None:
    case = load_case(CASES_DIR / "urs_pdf_real.yaml")
    run = run_case(case)
    assert run.classification is not None
    assert run.classification.c_closed == 34
    assert run.classification.total_variables == 43
    assert not run.classification.criterion_satisfied


def test_min_repair_requires_two_additions() -> None:
    case = load_case(CASES_DIR / "urs_pdf_repair.yaml")
    run = run_case(case)
    assert run.repair_result is not None
    assert run.repair_result.minimum_additions == 2
    assert len(run.repair_result.optimal_solutions) == 3
    for row in run.repair_result.optimal_solutions:
        assert row.metrics.fully_closed
        assert row.total_measured == 24


def test_yaml_round_trip_preserves_id(tmp_path: Path) -> None:
    original = load_case(CASES_DIR / "urs_pdf_real.yaml")
    out = tmp_path / "roundtrip.yaml"
    save_case(original, out)
    reloaded = load_case(out)
    assert reloaded.case_id == original.case_id
    assert reloaded.equations == original.equations

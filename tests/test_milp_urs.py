#!/usr/bin/env python3
"""MILP URS document placement tests (additive; tearing regressions unchanged)."""

from __future__ import annotations

from structural_obs import PROJECT_ROOT
from structural_obs.toolkit.milp.documento_ilp import explain_milp_conflicts
from structural_obs.toolkit.premises import IDEAL_MEASURED_PDF, REAL_MEASURED_PDF
from structural_obs.toolkit.schemas.loaders import load_case
from structural_obs.toolkit.services.classify_service import run_case
from structural_obs.tearing.cases.urs_document_bank import equations_documento

CASES_DIR = PROJECT_ROOT / "cases"

EXPECTED_GLOBAL_SENSORS = (
    "F",
    "PA",
    "PE",
    "Pa_C",
    "Pb_B",
    "Pb_D",
    "Pc_C",
    "Pc_D",
    "Rb_A",
    "Rb_E",
    "Rc_B",
)


def test_milp_global_optimal_eleven_sensors() -> None:
    case = load_case(CASES_DIR / "urs_milp_global.yaml")
    run = run_case(case)
    assert run.milp_summary is not None
    assert run.milp_result is not None
    summary = run.milp_summary
    assert summary.status == "optimal"
    assert summary.sensor_count == 11
    assert summary.measured == EXPECTED_GLOBAL_SENSORS
    assert run.classification is not None
    assert summary.tearing_c_closed is not None
    assert summary.tearing_total == 43


def test_milp_verify_ideal_infeasible() -> None:
    case = load_case(CASES_DIR / "urs_milp_verify_ideal.yaml")
    run = run_case(case)
    assert run.milp_summary is not None
    assert run.milp_summary.status == "infeasible"
    assert run.milp_summary.conflicts
    issues = explain_milp_conflicts(equations_documento(), set(IDEAL_MEASURED_PDF))
    assert len(issues) >= 1


def test_milp_verify_real_infeasible() -> None:
    case = load_case(CASES_DIR / "urs_milp_verify_real.yaml")
    run = run_case(case)
    assert run.milp_summary is not None
    assert run.milp_summary.status == "infeasible"
    assert run.milp_summary.conflicts
    issues = explain_milp_conflicts(equations_documento(), set(REAL_MEASURED_PDF))
    assert len(issues) >= 1


def test_milp_repair_real_base_infeasible_under_rules() -> None:
    """PDF real base cannot reach a feasible MILP solution with failed candidates only."""
    case = load_case(CASES_DIR / "urs_milp_repair.yaml")
    run = run_case(case)
    assert run.milp_summary is not None
    assert run.milp_summary.status == "infeasible"
    assert run.milp_summary.sensor_count == 0
    assert run.milp_summary.conflicts
    assert any("base fixa" in line for line in run.milp_summary.conflicts)

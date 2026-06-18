#!/usr/bin/env python3
"""Tests for min_placement (automatic sensor discovery for C_cl == |V|)."""

from __future__ import annotations

from structural_obs import PROJECT_ROOT
from structural_obs.toolkit.schemas.loaders import load_case
from structural_obs.toolkit.services.classify_service import run_case

CASES_DIR = PROJECT_ROOT / "cases"


def test_placement_real_base_finds_k2() -> None:
    """With 22 real base sensors, automatic placement should find k=2."""
    case = load_case(CASES_DIR / "urs_min_placement_real.yaml")
    run = run_case(case)
    assert run.objective == "min_placement"
    assert run.repair_result is not None
    result = run.repair_result
    assert result.minimum_additions == 2
    assert len(result.optimal_solutions) >= 1
    for row in result.optimal_solutions:
        assert row.metrics.fully_closed
        assert row.metrics.c_closed == row.metrics.total_variables


def test_placement_real_base_includes_ra_pairs() -> None:
    """Optimal solutions should include Ra_C/Ra_D/Ra_E pairs (PDF repair target)."""
    case = load_case(CASES_DIR / "urs_min_placement_real.yaml")
    run = run_case(case)
    assert run.repair_result is not None
    result = run.repair_result
    ra_target = {"Ra_C", "Ra_D", "Ra_E"}
    has_ra_pair = any(
        set(row.added).issubset(ra_target)
        for row in result.optimal_solutions
    )
    assert has_ra_pair, (
        "Expected at least one solution using Ra_C/Ra_D/Ra_E pairs; "
        f"found: {[row.added for row in result.optimal_solutions]}"
    )


def test_placement_real_all_solutions_valid() -> None:
    """Every optimal solution must achieve full coverage C_cl = 43/43."""
    case = load_case(CASES_DIR / "urs_min_placement_real.yaml")
    run = run_case(case)
    assert run.repair_result is not None
    for row in run.repair_result.optimal_solutions:
        assert row.metrics.fully_closed
        assert row.metrics.c_closed == 43


def test_placement_result_has_repair_rows() -> None:
    """CaseRunResult should include repair_rows with baseline + evaluated."""
    case = load_case(CASES_DIR / "urs_min_placement_real.yaml")
    run = run_case(case)
    assert run.repair_rows is not None
    assert len(run.repair_rows) >= 2
    baseline = run.repair_rows[0]
    assert baseline.search_kind == "baseline"
    assert baseline.base_count == 22


def test_placement_yaml_loads_correctly() -> None:
    """Both placement YAML files should load and validate without errors."""
    for name in ("urs_min_placement_real.yaml", "urs_min_placement_zero.yaml"):
        case = load_case(CASES_DIR / name)
        assert case.analysis.objective == "min_placement"
        assert case.analysis.criterion == "C_cl"


def test_placement_report_json_serializable() -> None:
    """Repair/placement export must not fail on frozenset fields."""
    import json

    from structural_obs.toolkit.services.audit_export import build_report_payload

    case = load_case(CASES_DIR / "urs_min_placement_real.yaml")
    run = run_case(case)
    payload = build_report_payload(run)
    json.dumps(payload)

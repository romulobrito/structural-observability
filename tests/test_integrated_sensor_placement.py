#!/usr/bin/env python3
"""Regression tests for integrated minimum instrumentation."""

from __future__ import annotations

from structural_obs.tearing.core import TearingConfig, classify_tearing
from structural_obs.tearing.registry import build_cases
from structural_obs.toolkit.services.candidate_generation import (
    generate_sensor_candidates,
)
from structural_obs.toolkit.services.integrated_sensor_placement import (
    solve_integrated_sensor_placement,
)

FAST_CONFIG = TearingConfig(
    time_limit_s=30.0,
    random_seed=42,
    require_optimal=True,
)


def _case(slug: str):
    return next(case for case in build_cases() if case.slug == slug)


def _allowed(case) -> dict[str, set[str]] | None:
    if case.allowed_outputs is None:
        return None
    return {
        equation: set(outputs)
        for equation, outputs in case.allowed_outputs.items()
    }


def test_integrated_urs_real_matches_exhaustive_minimum() -> None:
    case = _case("02_urs_real")
    equations = case.equations_fn()
    targets = {variable for values in equations.values() for variable in values}
    result = solve_integrated_sensor_placement(
        equations,
        set(case.measured),
        {"R", "Ra_C", "Ra_D", "Ra_E"},
        targets,
        case_name="test_urs_real",
        config=FAST_CONFIG,
    )
    valid_pairs = {
        frozenset({"Ra_C", "Ra_D"}),
        frozenset({"Ra_C", "Ra_E"}),
        frozenset({"Ra_D", "Ra_E"}),
    }
    assert result.minimum_certified
    assert result.selected_cost == 2
    assert frozenset(result.selected_sensors) in valid_pairs
    assert result.target_covered


def test_integrated_urs_real_respects_nonuniform_costs() -> None:
    case = _case("02_urs_real")
    equations = case.equations_fn()
    targets = {variable for values in equations.values() for variable in values}
    result = solve_integrated_sensor_placement(
        equations,
        set(case.measured),
        {"R", "Ra_C", "Ra_D", "Ra_E"},
        targets,
        sensor_costs={"Ra_C": 100, "Ra_D": 1, "Ra_E": 1, "R": 1},
        case_name="test_urs_real_cost",
        config=FAST_CONFIG,
    )
    assert result.minimum_certified
    assert set(result.selected_sensors) == {"Ra_D", "Ra_E"}
    assert result.selected_cost == 2


def test_integrated_reports_infeasible_candidate_set() -> None:
    case = _case("02_urs_real")
    equations = case.equations_fn()
    targets = {variable for values in equations.values() for variable in values}
    result = solve_integrated_sensor_placement(
        equations,
        set(case.measured),
        {"R"},
        targets,
        case_name="test_urs_real_infeasible",
        config=FAST_CONFIG,
    )
    assert not result.target_covered
    assert not result.minimum_certified
    assert result.status_by_phase["phase_1_min_sensor_cost"] == "INFEASIBLE"


def test_integrated_fixed_pattern_matches_frozen_classifier() -> None:
    case = _case("01_urs_ideal")
    equations = case.equations_fn()
    targets = {variable for values in equations.values() for variable in values}
    frozen = classify_tearing(
        equations,
        set(case.measured),
        case_name="test_fixed_frozen",
        config=FAST_CONFIG,
    )
    integrated = solve_integrated_sensor_placement(
        equations,
        set(case.measured),
        set(),
        targets,
        case_name="test_fixed_integrated",
        config=FAST_CONFIG,
    )
    assert integrated.minimum_certified
    assert integrated.selected_sensors == ()
    assert integrated.n_closed_coverage == frozen.n_closed_coverage
    assert integrated.n_external_reach == frozen.n_external_reach
    assert integrated.n_open_tears == len(frozen.tears_open)


def test_integrated_stage_kpis_selects_two_permeate_pressures() -> None:
    case = _case("13_urs_estagio")
    equations = case.equations_fn()
    allowed = _allowed(case)
    assert allowed is not None
    targets = set().union(*allowed.values())
    result = solve_integrated_sensor_placement(
        equations,
        set(case.measured),
        {"PT1_P", "PT2_P"},
        targets,
        known_constants=set(case.known_constants),
        allowed_outputs=allowed,
        case_name="test_stage_kpi",
        config=FAST_CONFIG,
    )
    assert result.minimum_certified
    assert set(result.selected_sensors) == {"PT1_P", "PT2_P"}
    assert result.target_covered


def test_integrated_bank_kpis_selects_nine_pressures() -> None:
    case = _case("17_urs_banco")
    equations = case.equations_fn()
    allowed = _allowed(case)
    assert allowed is not None
    targets = set().union(*allowed.values())
    candidates = {
        "PTa_F", "PTa_R", "PTa_P",
        "PTb_F", "PTb_R", "PTb_P",
        "PTc_F", "PTc_R", "PTc_P",
    }
    result = solve_integrated_sensor_placement(
        equations,
        set(case.measured),
        candidates,
        targets,
        known_constants=set(case.known_constants),
        allowed_outputs=allowed,
        case_name="test_bank_kpi",
        config=FAST_CONFIG,
    )
    assert result.minimum_certified
    assert set(result.selected_sensors) == candidates
    assert result.selected_cost == 9


def test_candidate_generation_uses_classification_gaps() -> None:
    case = _case("13_urs_estagio")
    equations = case.equations_fn()
    allowed = _allowed(case)
    assert allowed is not None
    targets = set().union(*allowed.values())
    baseline = classify_tearing(
        equations,
        set(case.measured),
        known_constants=set(case.known_constants),
        allowed_outputs=allowed,
        case_name="test_candidate_generation",
        config=FAST_CONFIG,
    )
    suggestions = generate_sensor_candidates(
        equations,
        baseline,
        targets,
        calculated_outputs=targets,
    )
    suggested = {item.variable for item in suggestions}
    assert {"PT1_P", "PT2_P"} <= suggested
    assert not (targets & suggested)

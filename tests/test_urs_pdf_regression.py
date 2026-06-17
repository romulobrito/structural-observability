#!/usr/bin/env python3
"""Regression tests for URS PDF minimum instrumentation scenarios."""

from __future__ import annotations

from structural_obs.tearing.core import TearingConfig
from structural_obs.toolkit.premises import IDEAL_MEASURED_PDF, REAL_MEASURED_PDF, repair_candidates
from structural_obs.toolkit.services.min_repair import evaluate_baseline, find_minimum_repair


def cfg() -> TearingConfig:
    return TearingConfig(time_limit_s=30, require_optimal=True)


def test_urs_ideal_full_closed_coverage() -> None:
    row = evaluate_baseline("ideal", set(IDEAL_MEASURED_PDF), cfg())
    assert row.metrics.c_closed == 43
    assert row.metrics.fully_closed


def test_urs_real_partial_closed_coverage() -> None:
    row = evaluate_baseline("real", set(REAL_MEASURED_PDF), cfg())
    assert row.metrics.c_closed == 34
    assert row.metrics.total_variables == 43
    assert not row.metrics.fully_closed


def test_urs_minimum_repair_requires_two_additions() -> None:
    result = find_minimum_repair(
        "real",
        set(REAL_MEASURED_PDF),
        repair_candidates("failed"),
        cfg(),
    )
    assert result.minimum_additions == 2
    assert len(result.optimal_solutions) == 3
    for row in result.optimal_solutions:
        assert row.metrics.fully_closed
        assert row.total_measured == 24


def main() -> None:
    for test in (
        test_urs_ideal_full_closed_coverage,
        test_urs_real_partial_closed_coverage,
        test_urs_minimum_repair_requires_two_additions,
    ):
        test()
        print(f"OK {test.__name__}")
    print("ALL_URS_PDF_TESTS_OK")


if __name__ == "__main__":
    main()

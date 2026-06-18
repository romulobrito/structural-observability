#!/usr/bin/env python3
"""Minimum instrumentation search under PDF premises using CP-SAT tearing metrics."""

from __future__ import annotations

import itertools
from dataclasses import asdict, dataclass
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

from structural_obs.tearing.cases.urs_document_bank import Equations, equations_documento
from structural_obs.tearing.core import TearingConfig, TearingResult, classify_tearing


@dataclass(frozen=True)
class CoverageMetrics:
    """Structural coverage summary for one measurement set."""

    total_variables: int
    c_closed: int
    c_external: int
    c_direct: int
    effective_indeterminate: int
    open_tears: int
    fully_closed: bool
    solver_status: str

    @property
    def closed_fraction(self) -> str:
        return f"{self.c_closed}/{self.total_variables}"


@dataclass(frozen=True)
class EvaluationRow:
    """One evaluated measurement configuration."""

    scenario_key: str
    base_count: int
    added: Tuple[str, ...]
    total_measured: int
    measured_sorted: Tuple[str, ...]
    metrics: CoverageMetrics
    search_kind: str


@dataclass(frozen=True)
class RepairSearchResult:
    """Result of minimum-cardinality repair from a fixed base."""

    scenario_key: str
    base_measured: FrozenSet[str]
    candidate_pool: Tuple[str, ...]
    minimum_additions: Optional[int]
    optimal_solutions: Tuple[EvaluationRow, ...]
    all_evaluated: Tuple[EvaluationRow, ...]


def _global_status(result: TearingResult) -> str:
    statuses = set(result.status_by_phase.values())
    return "OPTIMAL" if statuses == {"OPTIMAL"} else ",".join(sorted(statuses))


def evaluate_measured(
    equations: Equations,
    measured: Set[str],
    *,
    scenario_key: str,
    base_count: int,
    added: Sequence[str],
    search_kind: str,
    config: TearingConfig,
) -> EvaluationRow:
    """Classify one measurement set and extract coverage metrics."""
    result = classify_tearing(
        equations,
        set(measured),
        case_name=f"{scenario_key}+{'+'.join(added) if added else 'base'}",
        config=config,
    )
    metrics = CoverageMetrics(
        total_variables=result.total_variables,
        c_closed=result.n_closed_coverage,
        c_external=result.n_external_reach,
        c_direct=result.n_direct,
        effective_indeterminate=len(result.effective_indeterminate),
        open_tears=len(result.tears_open),
        fully_closed=result.n_closed_coverage == result.total_variables,
        solver_status=_global_status(result),
    )
    return EvaluationRow(
        scenario_key=scenario_key,
        base_count=base_count,
        added=tuple(sorted(added)),
        total_measured=len(measured),
        measured_sorted=tuple(sorted(measured)),
        metrics=metrics,
        search_kind=search_kind,
    )


def evaluate_baseline(
    scenario_key: str,
    base_measured: Set[str],
    config: TearingConfig,
    *,
    equations: Optional[Equations] = None,
) -> EvaluationRow:
    """Evaluate the PDF base set without additions."""
    eqs = equations_documento() if equations is None else equations
    return evaluate_measured(
        eqs,
        set(base_measured),
        scenario_key=scenario_key,
        base_count=len(base_measured),
        added=(),
        search_kind="baseline",
        config=config,
    )


def find_minimum_repair(
    scenario_key: str,
    base_measured: Set[str],
    candidates: Sequence[str],
    config: TearingConfig,
    *,
    equations: Optional[Equations] = None,
    max_additions: Optional[int] = None,
) -> RepairSearchResult:
    """Find minimum additional sensors from candidates to reach full closed coverage.

    Objective (lexicographic):
      1) minimize number of added sensors;
      2) among ties, keep all optimal combinations.
    Feasibility criterion: C_cl == |V| (fully closed structural coverage).
    """
    eqs = equations_documento() if equations is None else equations
    base_frozen = frozenset(base_measured)
    pool = tuple(v for v in candidates if v not in base_frozen)
    limit = max_additions if max_additions is not None else len(pool)

    evaluated: List[EvaluationRow] = []
    optimal: List[EvaluationRow] = []
    minimum_k: Optional[int] = None

    for k in range(1, limit + 1):
        found_at_k: List[EvaluationRow] = []
        for combo in itertools.combinations(pool, k):
            measured = set(base_measured) | set(combo)
            row = evaluate_measured(
                eqs,
                measured,
                scenario_key=scenario_key,
                base_count=len(base_measured),
                added=combo,
                search_kind="repair_search",
                config=config,
            )
            evaluated.append(row)
            if row.metrics.fully_closed:
                found_at_k.append(row)
        if found_at_k:
            minimum_k = k
            optimal = found_at_k
            break

    return RepairSearchResult(
        scenario_key=scenario_key,
        base_measured=base_frozen,
        candidate_pool=pool,
        minimum_additions=minimum_k,
        optimal_solutions=tuple(optimal),
        all_evaluated=tuple(evaluated),
    )


def find_minimum_placement(
    scenario_key: str,
    base_measured: Set[str],
    config: TearingConfig,
    *,
    equations: Optional[Equations] = None,
    max_additions: Optional[int] = None,
) -> RepairSearchResult:
    """Find minimum sensors to reach C_cl == |V| with automatic candidate discovery.

    Search phases (in order):
      Phase 1: candidates = effective_indeterminate (not in base), if pool is small.
      Phase 2: candidates = tears_open (minimal tear cuts).
      Phase 3: candidates = vars in equations that contain tears or indeterminate vars.
      Fallback: all non-base variables (capped by max_additions).

    ``max_additions`` caps the search depth (default 4).  Larger values may
    cause very long runtimes due to combinatorial explosion.
    """
    default_cap = 4
    max_auto_pool = 15
    cap = max_additions if max_additions is not None else default_cap

    eqs = equations_documento() if equations is None else equations
    all_vars = {v for vs in eqs.values() for v in vs}
    base = set(base_measured)
    non_base = sorted(all_vars - base)

    if not non_base:
        baseline = evaluate_baseline(scenario_key, base, config, equations=eqs)
        return RepairSearchResult(
            scenario_key=scenario_key,
            base_measured=frozenset(base),
            candidate_pool=(),
            minimum_additions=0 if baseline.metrics.fully_closed else None,
            optimal_solutions=(baseline,) if baseline.metrics.fully_closed else (),
            all_evaluated=(baseline,),
        )

    baseline_result = classify_tearing(
        eqs, base, case_name=f"{scenario_key}_placement_baseline", config=config,
    )

    if baseline_result.n_closed_coverage == baseline_result.total_variables:
        baseline_row = evaluate_baseline(scenario_key, base, config, equations=eqs)
        return RepairSearchResult(
            scenario_key=scenario_key,
            base_measured=frozenset(base),
            candidate_pool=tuple(non_base),
            minimum_additions=0,
            optimal_solutions=(baseline_row,),
            all_evaluated=(baseline_row,),
        )

    indeterminate = sorted(set(baseline_result.effective_indeterminate) - base)
    tears = sorted(set(baseline_result.tears_open) - base)

    def _safe_repair(pool: Sequence[str]) -> Optional[RepairSearchResult]:
        """Run find_minimum_repair catching solver failures on edge cases."""
        if not pool:
            return None
        try:
            return find_minimum_repair(
                scenario_key, base, pool, config,
                equations=eqs, max_additions=cap,
            )
        except RuntimeError:
            return None

    if indeterminate and len(indeterminate) <= max_auto_pool:
        result_indet = _safe_repair(indeterminate)
        if result_indet is not None and result_indet.minimum_additions is not None:
            return result_indet

    if tears and len(tears) <= max_auto_pool:
        result_tears = _safe_repair(tears)
        if result_tears is not None and result_tears.minimum_additions is not None:
            return result_tears

    seed = set(baseline_result.effective_indeterminate) | set(baseline_result.tears_open)
    expanded: Set[str] = set()
    for _eq_name, eq_vars in eqs.items():
        if seed & set(eq_vars):
            expanded.update(eq_vars)
    expanded -= base
    phase3_pool = sorted(expanded)

    if phase3_pool and len(phase3_pool) <= max_auto_pool:
        result_p3 = _safe_repair(phase3_pool)
        if result_p3 is not None and result_p3.minimum_additions is not None:
            return result_p3

    full_pool = sorted(all_vars - base)

    if len(full_pool) <= max_auto_pool:
        result_full = _safe_repair(full_pool)
        if result_full is not None:
            return result_full

    return RepairSearchResult(
        scenario_key=scenario_key,
        base_measured=frozenset(base),
        candidate_pool=tuple(indeterminate or tears or full_pool),
        minimum_additions=None,
        optimal_solutions=(),
        all_evaluated=(),
    )


def find_redundant_sensors(
    scenario_key: str,
    starting_measured: Set[str],
    config: TearingConfig,
) -> Tuple[EvaluationRow, List[str]]:
    """List sensors whose single removal preserves full closed coverage."""
    equations = equations_documento()
    baseline = evaluate_baseline(scenario_key, starting_measured, config)
    redundant: List[str] = []
    if not baseline.metrics.fully_closed:
        return baseline, redundant

    for sensor in sorted(starting_measured):
        reduced = set(starting_measured) - {sensor}
        row = evaluate_measured(
            equations,
            reduced,
            scenario_key=scenario_key,
            base_count=len(starting_measured),
            added=(),
            search_kind="redundancy_drop_one",
            config=config,
        )
        if row.metrics.fully_closed:
            redundant.append(sensor)
    return baseline, redundant


def greedy_minimum_subset(
    scenario_key: str,
    starting_measured: Set[str],
    config: TearingConfig,
) -> Tuple[Set[str], List[EvaluationRow]]:
    """Greedy removal of redundant sensors while preserving C_cl == |V|.

    Returns the reduced measurement set and the audit trail of accepted removals.
    """
    equations = equations_documento()
    current = set(starting_measured)
    trail: List[EvaluationRow] = []

    changed = True
    while changed:
        changed = False
        for sensor in sorted(current):
            trial = set(current) - {sensor}
            row = evaluate_measured(
                equations,
                trial,
                scenario_key=scenario_key,
                base_count=len(starting_measured),
                added=(),
                search_kind="greedy_min_subset",
                config=config,
            )
            if row.metrics.fully_closed:
                current = trial
                trail.append(row)
                changed = True
                break
    return current, trail


def row_to_dict(row: EvaluationRow) -> Dict[str, object]:
    """Serialize one evaluation row for JSON/CSV export."""
    payload = asdict(row)
    payload["metrics"] = asdict(row.metrics)
    return payload

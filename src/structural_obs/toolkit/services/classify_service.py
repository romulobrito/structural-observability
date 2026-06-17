#!/usr/bin/env python3
"""Run classification or minimum repair from a validated CaseDefinition."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set

from structural_obs.tearing.core import TearingConfig, TearingResult, classify_tearing
from structural_obs.toolkit.premises import repair_candidates
from structural_obs.toolkit.schemas.case_schema import CaseDefinition, Criterion, Objective
from structural_obs.toolkit.services.min_repair import (
    CoverageMetrics,
    EvaluationRow,
    RepairSearchResult,
    evaluate_measured,
    find_minimum_repair,
)


@dataclass(frozen=True)
class ClassificationSummary:
    """High-level metrics for one classification run."""

    case_id: str
    objective: Objective
    criterion: Criterion
    total_variables: int
    measured_count: int
    known_constants_count: int
    c_closed: int
    c_external: int
    c_direct: int
    effective_indeterminate: int
    open_tears: int
    criterion_satisfied: bool
    solver_status: str


@dataclass(frozen=True)
class CaseRunResult:
    """Unified result for YAML-driven case execution."""

    case: CaseDefinition
    objective: Objective
    classification: Optional[ClassificationSummary] = None
    tearing_result: Optional[TearingResult] = None
    repair_result: Optional[RepairSearchResult] = None
    repair_rows: Optional[tuple[EvaluationRow, ...]] = None


def tearing_config_from_case(case: CaseDefinition) -> TearingConfig:
    """Map case solver settings to TearingConfig."""
    solver = case.solver
    return TearingConfig(
        time_limit_s=solver.time_limit_s,
        require_optimal=solver.require_optimal,
        random_seed=solver.random_seed,
        use_structural_preprocessing=solver.use_structural_preprocessing,
    )


def _global_status(result: TearingResult) -> str:
    statuses = set(result.status_by_phase.values())
    return "OPTIMAL" if statuses == {"OPTIMAL"} else ",".join(sorted(statuses))


def _criterion_satisfied(result: TearingResult, criterion: Criterion) -> bool:
    if criterion == "C_cl":
        return result.n_closed_coverage == result.total_variables
    return result.n_external_reach == result.total_variables


def _summary_from_tearing(
    case: CaseDefinition,
    result: TearingResult,
    measured_count: int,
) -> ClassificationSummary:
    return ClassificationSummary(
        case_id=case.case_id,
        objective=case.analysis.objective,
        criterion=case.analysis.criterion,
        total_variables=result.total_variables,
        measured_count=measured_count,
        known_constants_count=len(case.instrumentation.known_constants),
        c_closed=result.n_closed_coverage,
        c_external=result.n_external_reach,
        c_direct=result.n_direct,
        effective_indeterminate=len(result.effective_indeterminate),
        open_tears=len(result.tears_open),
        criterion_satisfied=_criterion_satisfied(result, case.analysis.criterion),
        solver_status=_global_status(result),
    )


def run_classification(case: CaseDefinition) -> CaseRunResult:
    """Classify variables for instrumentation defined in the case."""
    measured = set(case.instrumentation.measured)
    known = set(case.instrumentation.known_constants)
    config = tearing_config_from_case(case)
    allowed: Optional[Dict[str, Set[str]]] = None
    if case.allowed_outputs is not None:
        allowed = {eq: set(vars_set) for eq, vars_set in case.allowed_outputs.items()}
    result = classify_tearing(
        case.equations,
        measured,
        case_name=case.case_id,
        config=config,
        known_constants=known,
        allowed_outputs=allowed,
    )
    summary = _summary_from_tearing(case, result, len(measured))
    return CaseRunResult(
        case=case,
        objective="classify",
        classification=summary,
        tearing_result=result,
    )


def _resolve_repair_candidates(case: CaseDefinition) -> tuple[str, ...]:
    repair = case.analysis.repair
    if repair is None:
        raise ValueError("min_repair requires analysis.repair")
    if repair.candidates:
        return repair.candidates
    return tuple(repair_candidates(repair.candidate_pool))


def run_minimum_repair(case: CaseDefinition) -> CaseRunResult:
    """Search minimum sensor additions to satisfy C_cl == |V|."""
    repair = case.analysis.repair
    if repair is None:
        raise ValueError("min_repair requires analysis.repair")
    config = tearing_config_from_case(case)
    base = set(repair.base_measured)
    candidates = _resolve_repair_candidates(case)
    search = find_minimum_repair(
        case.case_id,
        base,
        candidates,
        config,
        equations=case.equations,
        max_additions=repair.max_additions,
    )
    baseline_row = evaluate_measured(
        case.equations,
        base,
        scenario_key=case.case_id,
        base_count=len(base),
        added=(),
        search_kind="baseline",
        config=config,
    )
    return CaseRunResult(
        case=case,
        objective="min_repair",
        repair_result=search,
        repair_rows=(baseline_row,) + search.all_evaluated,
    )


def run_case(case: CaseDefinition) -> CaseRunResult:
    """Dispatch execution according to case.analysis.objective."""
    if case.analysis.objective == "classify":
        return run_classification(case)
    if case.analysis.objective == "min_repair":
        return run_minimum_repair(case)
    raise ValueError(f"Unsupported objective: {case.analysis.objective}")


def summary_to_dict(summary: ClassificationSummary) -> Dict[str, Any]:
    """Serialize classification summary for JSON export."""
    return asdict(summary)


def tearing_result_to_dict(result: TearingResult) -> Dict[str, Any]:
    """Serialize tearing result for JSON export."""
    return asdict(result)


def repair_result_to_dict(result: RepairSearchResult) -> Dict[str, Any]:
    """Serialize repair search result for JSON export."""
    payload = asdict(result)
    payload["optimal_solutions"] = [
        asdict(row) | {"metrics": asdict(row.metrics)} for row in result.optimal_solutions
    ]
    payload["all_evaluated"] = [
        asdict(row) | {"metrics": asdict(row.metrics)} for row in result.all_evaluated
    ]
    return payload


def repair_rows_to_csv_rows(rows: List[EvaluationRow]) -> List[Dict[str, Any]]:
    """Flatten evaluation rows for CSV export."""
    flat: List[Dict[str, Any]] = []
    for row in rows:
        metrics: CoverageMetrics = row.metrics
        flat.append(
            {
                "scenario_key": row.scenario_key,
                "search_kind": row.search_kind,
                "base_count": row.base_count,
                "added": ", ".join(row.added),
                "total_measured": row.total_measured,
                "C_cl": metrics.c_closed,
                "V": metrics.total_variables,
                "C_ext": metrics.c_external,
                "C_dir": metrics.c_direct,
                "effective_indeterminate": metrics.effective_indeterminate,
                "open_tears": metrics.open_tears,
                "fully_closed": metrics.fully_closed,
                "solver_status": metrics.solver_status,
            }
        )
    return flat

#!/usr/bin/env python3
"""Run URS document MILP placement and optional tearing post-audit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from structural_obs.tearing.core import TearingResult, classify_tearing
from structural_obs.toolkit.milp.documento_ilp import (
    MilpPlacementResult,
    explain_milp_conflicts,
    solve_milp_placement,
)
from structural_obs.toolkit.premises import repair_candidates
from structural_obs.toolkit.schemas.case_schema import CaseDefinition, MilpObjective


@dataclass(frozen=True)
class MilpRunSummary:
    """High-level MILP placement outcome with optional tearing audit."""

    case_id: str
    objective: MilpObjective
    mode: str
    status: str
    status_code: int
    solver_name: str
    sensor_count: int
    measured: Tuple[str, ...]
    inferred: Tuple[str, ...]
    additions: Tuple[str, ...]
    redundancy_cost: float
    base_measured: Tuple[str, ...]
    conflicts: Tuple[str, ...]
    tearing_c_closed: Optional[int] = None
    tearing_total: Optional[int] = None
    tearing_criterion_satisfied: Optional[bool] = None
    tearing_solver_status: Optional[str] = None


def _objective_to_mode(objective: MilpObjective) -> str:
    mapping = {
        "milp_global": "global",
        "milp_repair": "repair",
        "milp_verify": "verify",
    }
    return mapping[objective]


def _resolve_repair_candidates(case: CaseDefinition) -> Tuple[str, ...]:
    repair = case.analysis.repair
    if repair is None:
        raise ValueError("milp_repair requires analysis.repair")
    if repair.candidates:
        return repair.candidates
    return tuple(repair_candidates(repair.candidate_pool))


def _build_milp_conflicts(
    case: CaseDefinition,
    objective: str,
    base: Set[str],
    candidates: Set[str],
    fixed: Optional[Set[str]],
) -> Tuple[str, ...]:
    """Assemble PT-BR conflict messages for infeasible MILP runs."""
    if objective == "milp_verify":
        check_set = fixed if fixed is not None else base
        return tuple(explain_milp_conflicts(case.equations, set(check_set)))

    if objective == "milp_repair":
        lines: List[str] = [
            "Não existe solução MILP mantendo a base fixa e instalando "
            "somente entre os candidatos permitidos."
        ]
        lines.extend(explain_milp_conflicts(case.equations, set(base)))
        if candidates:
            attempt = set(base) | set(candidates)
            attempt_issues = explain_milp_conflicts(case.equations, attempt)
            cand_text = ", ".join(sorted(candidates))
            if attempt_issues:
                lines.append(
                    f"Mesmo instalando todos os candidatos ({cand_text}), "
                    f"restam {len(attempt_issues)} conflito(s) com as regras."
                )
            else:
                lines.append(
                    f"Com todos os candidatos ({cand_text}) as regras fecham, "
                    f"mas o solver não encontrou solução ótima dentro dos limites."
                )
        return tuple(lines)

    return tuple(explain_milp_conflicts(case.equations, set(base)))


def _criterion_satisfied(result: TearingResult, criterion: str) -> bool:
    if criterion == "C_cl":
        return result.n_closed_coverage == result.total_variables
    return result.n_external_reach == result.total_variables


def _global_status(result: TearingResult) -> str:
    statuses = set(result.status_by_phase.values())
    return "OPTIMAL" if statuses == {"OPTIMAL"} else ",".join(sorted(statuses))


def _tearing_config_from_case(case: CaseDefinition):
    from structural_obs.toolkit.services.classify_service import tearing_config_from_case

    return tearing_config_from_case(case)


def _tearing_on_measured(
    case: CaseDefinition,
    measured: Set[str],
):
    from structural_obs.toolkit.services.classify_service import ClassificationSummary

    config = _tearing_config_from_case(case)
    known = set(case.instrumentation.known_constants)
    result = classify_tearing(
        case.equations,
        measured,
        case_name=f"{case.case_id}_milp_audit",
        config=config,
        known_constants=known,
    )
    summary = ClassificationSummary(
        case_id=case.case_id,
        objective=case.analysis.objective,
        criterion=case.analysis.criterion,
        total_variables=result.total_variables,
        measured_count=len(measured),
        known_constants_count=len(known),
        c_closed=result.n_closed_coverage,
        c_external=result.n_external_reach,
        c_direct=result.n_direct,
        effective_indeterminate=len(result.effective_indeterminate),
        open_tears=len(result.tears_open),
        criterion_satisfied=_criterion_satisfied(result, case.analysis.criterion),
        solver_status=_global_status(result),
    )
    return result, summary


def _summary_from_milp(
    case: CaseDefinition,
    placement: MilpPlacementResult,
    *,
    conflicts: Tuple[str, ...] = (),
    tearing: Optional[TearingResult] = None,
    tearing_summary=None,
) -> MilpRunSummary:
    tearing_c: Optional[int] = None
    tearing_v: Optional[int] = None
    tearing_ok: Optional[bool] = None
    tearing_status: Optional[str] = None
    if tearing is not None and tearing_summary is not None:
        tearing_c = tearing_summary.c_closed
        tearing_v = tearing_summary.total_variables
        tearing_ok = tearing_summary.criterion_satisfied
        tearing_status = tearing_summary.solver_status
    return MilpRunSummary(
        case_id=case.case_id,
        objective=case.analysis.objective,  # type: ignore[arg-type]
        mode=placement.mode,
        status=placement.status,
        status_code=placement.status_code,
        solver_name=placement.solver_name,
        sensor_count=placement.sensor_count,
        measured=placement.measured,
        inferred=placement.inferred,
        additions=placement.additions,
        redundancy_cost=placement.redundancy_cost,
        base_measured=placement.base_measured,
        conflicts=conflicts,
        tearing_c_closed=tearing_c,
        tearing_total=tearing_v,
        tearing_criterion_satisfied=tearing_ok,
        tearing_solver_status=tearing_status,
    )


def run_milp(case: CaseDefinition):
    """Execute MILP placement for milp_global, milp_repair, or milp_verify."""
    from structural_obs.toolkit.services.classify_service import CaseRunResult

    objective = case.analysis.objective
    if objective not in ("milp_global", "milp_repair", "milp_verify"):
        raise ValueError(f"Not a MILP objective: {objective}")

    mode = _objective_to_mode(objective)  # type: ignore[arg-type]
    base: Set[str] = set()
    candidates: Set[str] = set()
    fixed: Optional[Set[str]] = None

    if objective == "milp_repair":
        repair = case.analysis.repair
        if repair is None:
            raise ValueError("milp_repair requires analysis.repair")
        base = set(repair.base_measured)
        candidates = set(_resolve_repair_candidates(case))
    elif objective == "milp_verify":
        fixed = set(case.instrumentation.measured)
        base = fixed

    placement = solve_milp_placement(
        case.equations,
        mode,  # type: ignore[arg-type]
        base_measured=base,
        candidates=candidates,
        fixed_measured=fixed,
    )

    conflicts: Tuple[str, ...] = ()
    tearing_result: Optional[TearingResult] = None
    tearing_summary = None

    if placement.status in ("optimal", "feasible") and placement.measured:
        measured_set = set(placement.measured)
        tearing_result, tearing_summary = _tearing_on_measured(case, measured_set)
    elif placement.status == "infeasible":
        conflicts = _build_milp_conflicts(case, objective, base, candidates, fixed)

    summary = _summary_from_milp(
        case,
        placement,
        conflicts=conflicts,
        tearing=tearing_result,
        tearing_summary=tearing_summary,
    )

    return CaseRunResult(
        case=case,
        objective=objective,  # type: ignore[arg-type]
        milp_result=placement,
        milp_summary=summary,
        tearing_result=tearing_result,
        classification=tearing_summary,
    )


def milp_summary_to_dict(summary: MilpRunSummary) -> Dict[str, Any]:
    """Serialize MILP summary for JSON export."""
    return asdict(summary)


def milp_result_to_dict(result: MilpPlacementResult) -> Dict[str, Any]:
    """Serialize MILP placement for JSON export."""
    return asdict(result)

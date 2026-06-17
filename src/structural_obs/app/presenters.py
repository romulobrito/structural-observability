#!/usr/bin/env python3
"""Map engine results to simple UI view models (no Streamlit dependency)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Sequence, Tuple

from structural_obs.app.ui_labels import (
    SOLVER_CONFIRMED,
    SOLVER_OTHER,
    VAR_STATUS_BY_CLASS,
    VAR_STATUS_NOT_CALCULABLE,
)
from structural_obs.tearing.core import TearingResult
from structural_obs.toolkit.schemas.case_schema import AnalysisConfig, InstrumentationConfig
from structural_obs.toolkit.services.classify_service import CaseRunResult, run_classification
from structural_obs.toolkit.services.min_repair import EvaluationRow


@dataclass(frozen=True)
class StatusGroup:
    """Variables grouped by simple status label."""

    label: str
    tags: Tuple[str, ...]


@dataclass(frozen=True)
class ClassificationMetrics:
    """Summary counters for classification display."""

    calculable: int
    total: int
    not_calculable: int
    measured_count: int
    known_constants_count: int
    direct_count: int
    external_reach: int
    inferred_count: int
    indeterminate_count: int
    open_tears_count: int
    computes_all: bool
    solver_label: str


@dataclass(frozen=True)
class ClassificationView:
    """Simple-language view for classify objective."""

    headline: str
    metrics: ClassificationMetrics
    calculable_tags: Tuple[str, ...]
    not_calculable_tags: Tuple[str, ...]
    open_balance_tags: Tuple[str, ...]
    measured_tags: Tuple[str, ...]
    inferred_tags: Tuple[str, ...]
    status_groups: Tuple[StatusGroup, ...]
    variable_rows: Tuple[Dict[str, str], ...]


@dataclass(frozen=True)
class RepairOptionView:
    """One minimum-cardinality installation option."""

    option_id: int
    sensors_to_add: Tuple[str, ...]
    total_measured: int
    calculable: int
    total: int
    external_reach: int
    indeterminate_count: int
    open_tears_count: int
    computes_all: bool
    solver_label: str


@dataclass(frozen=True)
class RepairView:
    """Simple-language view for min_repair objective."""

    headline: str
    base_measured_count: int
    minimum_additions: Optional[int]
    total_after: Optional[int]
    solver_label: str
    options: Tuple[RepairOptionView, ...]
    baseline: ClassificationView
    baseline_tearing: Optional[TearingResult]
    candidates: Tuple[str, ...]


def solver_label(status: str) -> str:
    """Map solver status code to a simple user-facing label."""
    if status == "OPTIMAL":
        return SOLVER_CONFIRMED
    return SOLVER_OTHER


def _variable_rows(result: TearingResult) -> Tuple[Dict[str, str], ...]:
    """Build per-variable rows with simple status labels."""
    classes: Sequence[Tuple[str, Sequence[str]]] = (
        ("measured_sensor", result.measured),
        ("known_constant", result.known_constants),
        ("inferred_direct", result.inferred_direct),
        ("inferred_closed_loop", result.inferred_closed_loop),
        ("closed_tear", result.tears_closed),
        ("inferred_conditioned_open_tear", result.inferred_conditioned_open),
        ("closed_tear_external_dependency", result.tears_closed_external),
        ("open_tear", result.tears_open),
        ("pure_indeterminate", result.indeterminate_pure),
    )
    rows: List[Dict[str, str]] = []
    for class_key, variables in classes:
        label = VAR_STATUS_BY_CLASS.get(class_key, VAR_STATUS_NOT_CALCULABLE)
        for tag in sorted(variables):
            rows.append({"tag": tag, "status": label})
    return tuple(rows)


def _status_groups(rows: Tuple[Dict[str, str], ...]) -> Tuple[StatusGroup, ...]:
    """Group variable rows by status label preserving first-seen order."""
    order: List[str] = []
    buckets: Dict[str, List[str]] = {}
    for row in rows:
        label = row["status"]
        if label not in buckets:
            order.append(label)
            buckets[label] = []
        buckets[label].append(row["tag"])
    return tuple(
        StatusGroup(label=label, tags=tuple(sorted(buckets[label])))
        for label in order
        if buckets[label]
    )


def _inferred_tags(result: TearingResult) -> Tuple[str, ...]:
    """Tags calculable today but not measured or known constants."""
    initial = set(result.measured) | set(result.known_constants)
    inferred = result.closed_coverage_variables - initial
    return tuple(sorted(inferred))


def classification_headline(measured_count: int, calculable: int, total: int) -> str:
    """One-sentence summary for classify results."""
    if calculable == total:
        return (
            f"Com as {measured_count} medidas, calculamos todas as {total} grandezas."
        )
    return (
        f"Com as {measured_count} medidas, calculamos {calculable} de {total} grandezas."
    )


def repair_headline(minimum_additions: Optional[int], total: int) -> str:
    """One-sentence summary for min_repair results."""
    if minimum_additions is None:
        return (
            "Não encontramos medidores adicionais que permitam calcular "
            f"todas as {total} grandezas com os candidatos informados."
        )
    if minimum_additions == 1:
        word = "medidor"
    else:
        word = "medidores"
    return (
        f"Para calcular todas as {total} grandezas, faltam instalar "
        f"{minimum_additions} {word}."
    )


def _classification_view_from_tearing(
    result: TearingResult,
    *,
    measured_count: int,
    known_constants_count: int,
    criterion_satisfied: bool,
    solver_status: str,
) -> ClassificationView:
    rows = _variable_rows(result)
    calculable = result.n_closed_coverage
    total = result.total_variables
    return ClassificationView(
        headline=classification_headline(measured_count, calculable, total),
        metrics=ClassificationMetrics(
            calculable=calculable,
            total=total,
            not_calculable=total - calculable,
            measured_count=measured_count,
            known_constants_count=known_constants_count,
            direct_count=result.n_direct,
            external_reach=result.n_external_reach,
            inferred_count=len(_inferred_tags(result)),
            indeterminate_count=len(result.effective_indeterminate),
            open_tears_count=len(result.tears_open),
            computes_all=criterion_satisfied,
            solver_label=solver_label(solver_status),
        ),
        calculable_tags=tuple(sorted(result.closed_coverage_variables)),
        not_calculable_tags=tuple(sorted(result.effective_indeterminate)),
        open_balance_tags=tuple(sorted(result.tears_open)),
        measured_tags=tuple(sorted(result.measured)),
        inferred_tags=_inferred_tags(result),
        status_groups=_status_groups(rows),
        variable_rows=rows,
    )


def present_classification(run: CaseRunResult) -> ClassificationView:
    """Build a ClassificationView from a classify run."""
    if run.classification is None or run.tearing_result is None:
        raise ValueError("CaseRunResult is not a classification run")
    summary = run.classification
    return _classification_view_from_tearing(
        run.tearing_result,
        measured_count=summary.measured_count,
        known_constants_count=summary.known_constants_count,
        criterion_satisfied=summary.criterion_satisfied,
        solver_status=summary.solver_status,
    )


def _baseline_classification_run(run: CaseRunResult) -> CaseRunResult:
    """Classify the repair base set for before/after comparison."""
    repair = run.case.analysis.repair
    if repair is None:
        raise ValueError("Repair case missing analysis.repair")
    base_case = replace(
        run.case,
        instrumentation=InstrumentationConfig(
            measured=repair.base_measured,
            known_constants=run.case.instrumentation.known_constants,
        ),
        analysis=AnalysisConfig(
            objective="classify",
            criterion=run.case.analysis.criterion,
            repair=None,
        ),
    )
    return run_classification(base_case)


def _baseline_classification_view(run: CaseRunResult) -> Tuple[ClassificationView, Optional[TearingResult]]:
    baseline_run = _baseline_classification_run(run)
    return present_classification(baseline_run), baseline_run.tearing_result


def _option_result_label(calculable: int, total: int, computes_all: bool) -> str:
    if computes_all:
        return f"Calcula tudo ({calculable}/{total})"
    return f"Calcula {calculable} de {total}"


def present_repair(run: CaseRunResult) -> RepairView:
    """Build a RepairView from a min_repair run."""
    if run.repair_result is None or not run.repair_rows:
        raise ValueError("CaseRunResult is not a repair run")
    repair = run.repair_result
    baseline_row: EvaluationRow = run.repair_rows[0]
    total = baseline_row.metrics.total_variables
    options: List[RepairOptionView] = []
    for idx, row in enumerate(repair.optimal_solutions, start=1):
        metrics = row.metrics
        options.append(
            RepairOptionView(
                option_id=idx,
                sensors_to_add=row.added,
                total_measured=row.total_measured,
                calculable=metrics.c_closed,
                total=metrics.total_variables,
                external_reach=metrics.c_external,
                indeterminate_count=metrics.effective_indeterminate,
                open_tears_count=metrics.open_tears,
                computes_all=metrics.fully_closed,
                solver_label=solver_label(metrics.solver_status),
            )
        )
    base_count = len(repair.base_measured)
    min_k = repair.minimum_additions
    total_after = base_count + min_k if min_k is not None else None
    status = SOLVER_CONFIRMED
    if repair.optimal_solutions:
        status = repair.optimal_solutions[0].metrics.solver_status
        status = solver_label(status)
    elif baseline_row.metrics.solver_status != "OPTIMAL":
        status = solver_label(baseline_row.metrics.solver_status)
    baseline_view, baseline_tearing = _baseline_classification_view(run)
    return RepairView(
        headline=repair_headline(min_k, total),
        base_measured_count=base_count,
        minimum_additions=min_k,
        total_after=total_after,
        solver_label=status,
        options=tuple(options),
        baseline=baseline_view,
        baseline_tearing=baseline_tearing,
        candidates=repair.candidate_pool,
    )


def repair_option_table_rows(options: Sequence[RepairOptionView]) -> List[Dict[str, str]]:
    """Rows for the installation options table."""
    rows: List[Dict[str, str]] = []
    for opt in options:
        rows.append(
            {
                "option": str(opt.option_id),
                "install": ", ".join(opt.sensors_to_add),
                "total_measured": str(opt.total_measured),
                "result": _option_result_label(opt.calculable, opt.total, opt.computes_all),
                "indeterminate": str(opt.indeterminate_count),
                "open_tears": str(opt.open_tears_count),
            }
        )
    return rows

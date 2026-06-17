#!/usr/bin/env python3
"""Map engine results to simple UI view models (no Streamlit dependency)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from structural_obs.app.ui_labels import (
    SOLVER_CONFIRMED,
    SOLVER_OTHER,
    VAR_STATUS_BY_CLASS,
    VAR_STATUS_NOT_CALCULABLE,
)
from structural_obs.tearing.core import TearingResult
from structural_obs.toolkit.services.classify_service import CaseRunResult
from structural_obs.toolkit.services.min_repair import EvaluationRow


@dataclass(frozen=True)
class ClassificationView:
    """Simple-language view for classify objective."""

    headline: str
    calculable: int
    total: int
    not_calculable: int
    measured_count: int
    computes_all: bool
    solver_label: str
    calculable_tags: Tuple[str, ...]
    not_calculable_tags: Tuple[str, ...]
    open_balance_tags: Tuple[str, ...]
    variable_rows: Tuple[Dict[str, str], ...]


@dataclass(frozen=True)
class RepairOptionView:
    """One minimum-cardinality installation option."""

    option_id: int
    sensors_to_add: Tuple[str, ...]
    calculable: int
    total: int
    computes_all: bool


@dataclass(frozen=True)
class RepairView:
    """Simple-language view for min_repair objective."""

    headline: str
    base_measured_count: int
    minimum_additions: Optional[int]
    total_after: Optional[int]
    solver_label: str
    options: Tuple[RepairOptionView, ...]
    baseline_calculable: int
    baseline_total: int


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
            "Nao encontramos medidores adicionais que permitam calcular "
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


def present_classification(run: CaseRunResult) -> ClassificationView:
    """Build a ClassificationView from a classify run."""
    if run.classification is None or run.tearing_result is None:
        raise ValueError("CaseRunResult is not a classification run")
    summary = run.classification
    result = run.tearing_result
    calculable_tags = tuple(sorted(result.closed_coverage_variables))
    not_calculable_tags = tuple(sorted(result.effective_indeterminate))
    return ClassificationView(
        headline=classification_headline(
            summary.measured_count, summary.c_closed, summary.total_variables
        ),
        calculable=summary.c_closed,
        total=summary.total_variables,
        not_calculable=summary.total_variables - summary.c_closed,
        measured_count=summary.measured_count,
        computes_all=summary.criterion_satisfied,
        solver_label=solver_label(summary.solver_status),
        calculable_tags=calculable_tags,
        not_calculable_tags=not_calculable_tags,
        open_balance_tags=tuple(sorted(result.tears_open)),
        variable_rows=_variable_rows(result),
    )


def _option_result_label(calculable: int, total: int, computes_all: bool) -> str:
    if computes_all:
        return f"Calcula tudo ({calculable}/{total})"
    return f"Calcula {calculable} de {total}"


def present_repair(run: CaseRunResult) -> RepairView:
    """Build a RepairView from a min_repair run."""
    if run.repair_result is None or not run.repair_rows:
        raise ValueError("CaseRunResult is not a repair run")
    repair = run.repair_result
    baseline: EvaluationRow = run.repair_rows[0]
    total = baseline.metrics.total_variables
    options: List[RepairOptionView] = []
    for idx, row in enumerate(repair.optimal_solutions, start=1):
        options.append(
            RepairOptionView(
                option_id=idx,
                sensors_to_add=row.added,
                calculable=row.metrics.c_closed,
                total=row.metrics.total_variables,
                computes_all=row.metrics.fully_closed,
            )
        )
    base_count = len(repair.base_measured)
    min_k = repair.minimum_additions
    total_after = base_count + min_k if min_k is not None else None
    status = SOLVER_CONFIRMED
    if repair.optimal_solutions:
        status = solver_label(repair.optimal_solutions[0].metrics.solver_status)
    elif baseline.metrics.solver_status != "OPTIMAL":
        status = solver_label(baseline.metrics.solver_status)
    return RepairView(
        headline=repair_headline(min_k, total),
        base_measured_count=base_count,
        minimum_additions=min_k,
        total_after=total_after,
        solver_label=status,
        options=tuple(options),
        baseline_calculable=baseline.metrics.c_closed,
        baseline_total=total,
    )


def repair_option_table_rows(options: Sequence[RepairOptionView]) -> List[Dict[str, str]]:
    """Rows for the installation options table."""
    rows: List[Dict[str, str]] = []
    for opt in options:
        rows.append(
            {
                "option": str(opt.option_id),
                "install": ", ".join(opt.sensors_to_add),
                "result": _option_result_label(opt.calculable, opt.total, opt.computes_all),
            }
        )
    return rows

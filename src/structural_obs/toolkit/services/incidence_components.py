#!/usr/bin/env python3
"""Partition incidence graphs and aggregate independent solver results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Set

from structural_obs.tearing.core import TearingResult, validate_result
from structural_obs.toolkit.services.integrated_sensor_placement import (
    IntegratedPlacementResult,
)

Equations = Dict[str, List[str]]


@dataclass(frozen=True)
class IncidenceComponent:
    """One connected component of the equation-variable incidence graph."""

    component_id: str
    equations: Equations
    variables: frozenset[str]


def partition_incidence_components(
    equations: Mapping[str, Sequence[str]],
) -> tuple[IncidenceComponent, ...]:
    """Return deterministic connected components without domain assumptions."""

    variable_equations: dict[str, set[str]] = {}
    for equation, values in equations.items():
        for variable in set(values):
            variable_equations.setdefault(variable, set()).add(equation)

    unseen_equations = set(equations)
    components: list[tuple[set[str], set[str]]] = []
    while unseen_equations:
        root = min(unseen_equations)
        pending_equations = [root]
        component_equations: set[str] = set()
        component_variables: set[str] = set()
        while pending_equations:
            equation = pending_equations.pop()
            if equation in component_equations:
                continue
            component_equations.add(equation)
            unseen_equations.discard(equation)
            for variable in equations[equation]:
                if variable in component_variables:
                    continue
                component_variables.add(variable)
                pending_equations.extend(
                    sorted(variable_equations.get(variable, set()))
                )
        components.append((component_equations, component_variables))

    components.sort(
        key=lambda item: (
            -len(item[1]),
            min(item[0]),
        )
    )
    return tuple(
        IncidenceComponent(
            component_id=f"component_{index:03d}",
            equations={
                name: list(equations[name])
                for name in sorted(equation_names)
            },
            variables=frozenset(variables),
        )
        for index, (equation_names, variables) in enumerate(components, start=1)
    )


def project_allowed_outputs(
    allowed_outputs: Mapping[str, Set[str]] | None,
    component: IncidenceComponent,
) -> dict[str, set[str]] | None:
    """Project allowed outputs onto one component."""

    if allowed_outputs is None:
        return None
    projected = {
        equation: set(outputs) & set(component.variables)
        for equation, outputs in allowed_outputs.items()
        if equation in component.equations
    }
    return projected or None


def _merged_status(statuses: Iterable[str]) -> str:
    values = set(statuses)
    if values == {"OPTIMAL"}:
        return "OPTIMAL"
    if values <= {"OPTIMAL", "FEASIBLE"}:
        return "FEASIBLE"
    if "UNKNOWN" in values:
        return "UNKNOWN"
    if "INFEASIBLE" in values:
        return "INFEASIBLE"
    return ",".join(sorted(values))


def merge_tearing_results(
    case_name: str,
    parts: Sequence[TearingResult],
) -> TearingResult:
    """Merge independent classifications and validate the global partition."""

    if not parts:
        raise ValueError("At least one classification part is required")
    phase_names = sorted(
        set().union(*(set(part.status_by_phase) for part in parts))
    )
    statuses = {
        phase: _merged_status(
            part.status_by_phase.get(phase, "UNKNOWN")
            for part in parts
        )
        for phase in phase_names
    }
    objectives = {
        phase: sum(
            part.objective_by_phase.get(phase, 0.0)
            for part in parts
        )
        for phase in phase_names
        if all(phase in part.objective_by_phase for part in parts)
    }
    times = {
        phase: sum(
            part.time_by_phase_s.get(phase, 0.0)
            for part in parts
        )
        for phase in phase_names
    }

    def merged_list(attribute: str) -> list[str]:
        return sorted(
            value
            for part in parts
            for value in getattr(part, attribute)
        )

    output_equation = {
        variable: equation
        for part in parts
        for variable, equation in part.output_equation.items()
    }
    output_uses_tears = {
        variable: list(values)
        for part in parts
        for variable, values in part.output_uses_tears.items()
    }
    levels = {
        variable: level
        for part in parts
        for variable, level in part.levels.items()
    }
    result = TearingResult(
        case_name=case_name,
        total_variables=sum(part.total_variables for part in parts),
        total_equations=sum(part.total_equations for part in parts),
        total_incidences=sum(part.total_incidences for part in parts),
        model_equations=sum(part.model_equations for part in parts),
        model_incidences=sum(part.model_incidences for part in parts),
        structural_rank=sum(part.structural_rank for part in parts),
        preprocessing_enabled=all(part.preprocessing_enabled for part in parts),
        retained_equations=merged_list("retained_equations"),
        removed_equations=merged_list("removed_equations"),
        measured=merged_list("measured"),
        known_constants=merged_list("known_constants"),
        inferred_direct=merged_list("inferred_direct"),
        inferred_closed_loop=merged_list("inferred_closed_loop"),
        tears_closed=merged_list("tears_closed"),
        inferred_conditioned_open=merged_list("inferred_conditioned_open"),
        tears_closed_external=merged_list("tears_closed_external"),
        tears_open=merged_list("tears_open"),
        indeterminate_pure=merged_list("indeterminate_pure"),
        effective_indeterminate=merged_list("effective_indeterminate"),
        tear_pairs=sorted(
            pair
            for part in parts
            for pair in part.tear_pairs
        ),
        output_equation=dict(sorted(output_equation.items())),
        output_uses_tears=dict(sorted(output_uses_tears.items())),
        levels=dict(sorted(levels.items())),
        status_by_phase=statuses,
        objective_by_phase=objectives,
        time_by_phase_s=times,
        execution_graph_is_dag=all(
            part.execution_graph_is_dag for part in parts
        ),
        cyclic_sccs_full_graph=sorted(
            component
            for part in parts
            for component in part.cyclic_sccs_full_graph
        ),
        cut_graph_edges=sorted(
            edge
            for part in parts
            for edge in part.cut_graph_edges
        ),
        full_graph_edges=sorted(
            edge
            for part in parts
            for edge in part.full_graph_edges
        ),
        externally_conditioned=merged_list("externally_conditioned"),
    )
    validate_result(result)
    return result


def merge_placement_results(
    case_name: str,
    parts: Sequence[IntegratedPlacementResult],
    *,
    baseline_parts_without_targets: Sequence[TearingResult] = (),
) -> IntegratedPlacementResult:
    """Merge independent placement certificates conservatively."""

    if not parts:
        raise ValueError("At least one placement part is required")
    phase_names = sorted(
        set().union(*(set(part.status_by_phase) for part in parts))
    )
    statuses = {
        phase: _merged_status(
            part.status_by_phase.get(phase, "UNKNOWN")
            for part in parts
        )
        for phase in phase_names
    }
    objectives = {
        phase: sum(
            part.objective_by_phase.get(phase, 0.0)
            for part in parts
        )
        for phase in phase_names
        if all(phase in part.objective_by_phase for part in parts)
    }
    times = {
        phase: sum(
            part.time_by_phase_s.get(phase, 0.0)
            for part in parts
        )
        for phase in phase_names
    }
    return IntegratedPlacementResult(
        case_name=case_name,
        selected_sensors=tuple(sorted(
            sensor
            for part in parts
            for sensor in part.selected_sensors
        )),
        selected_cost=sum(part.selected_cost for part in parts),
        minimum_certified=all(part.minimum_certified for part in parts),
        target_variables=tuple(sorted(
            target
            for part in parts
            for target in part.target_variables
        )),
        target_covered=all(part.target_covered for part in parts),
        n_closed_coverage=(
            sum(part.n_closed_coverage for part in parts)
            + sum(
                part.n_closed_coverage
                for part in baseline_parts_without_targets
            )
        ),
        n_external_reach=(
            sum(part.n_external_reach for part in parts)
            + sum(
                part.n_external_reach
                for part in baseline_parts_without_targets
            )
        ),
        n_open_tears=(
            sum(part.n_open_tears for part in parts)
            + sum(
                len(part.tears_open)
                for part in baseline_parts_without_targets
            )
        ),
        n_raw_tears=(
            sum(part.n_raw_tears for part in parts)
            + sum(
                len(part.tear_pairs)
                for part in baseline_parts_without_targets
            )
        ),
        status_by_phase=statuses,
        objective_by_phase=objectives,
        time_by_phase_s=times,
        retained_equations=tuple(sorted(
            equation
            for part in parts
            for equation in part.retained_equations
        )),
        removed_equations=tuple(sorted(
            equation
            for part in parts
            for equation in part.removed_equations
        )),
    )

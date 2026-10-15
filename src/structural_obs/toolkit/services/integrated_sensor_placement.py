#!/usr/bin/env python3
"""Integrated CP-SAT model for minimum structural instrumentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple

from ortools.sat.python import cp_model

from structural_obs.tearing.core import (
    Equations,
    TearingConfig,
    all_variables,
    preprocess_equations_structural,
)


@dataclass(frozen=True)
class IntegratedPlacementResult:
    """Auditable result from integrated sensor placement."""

    case_name: str
    selected_sensors: tuple[str, ...]
    selected_cost: int
    minimum_certified: bool
    target_variables: tuple[str, ...]
    target_covered: bool
    n_closed_coverage: int
    n_external_reach: int
    n_open_tears: int
    n_raw_tears: int
    status_by_phase: Mapping[str, str]
    objective_by_phase: Mapping[str, float]
    time_by_phase_s: Mapping[str, float]
    retained_equations: tuple[str, ...]
    removed_equations: tuple[str, ...]


@dataclass(frozen=True)
class _PlacementSnapshot:
    selected: tuple[str, ...]
    selected_cost: int
    target_covered: bool
    n_closed: int
    n_external: int
    n_open: int
    n_raw: int


def _solver(config: TearingConfig) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = config.time_limit_s
    solver.parameters.random_seed = config.random_seed
    solver.parameters.num_search_workers = max(1, int(config.num_search_workers))
    solver.parameters.randomize_search = False
    return solver


def solve_integrated_sensor_placement(
    equations: Equations,
    base_measured: Set[str],
    candidates: Set[str],
    targets: Set[str],
    *,
    known_constants: Optional[Set[str]] = None,
    allowed_outputs: Optional[Mapping[str, Set[str]]] = None,
    sensor_costs: Optional[Mapping[str, int]] = None,
    case_name: str = "integrated_placement",
    config: Optional[TearingConfig] = None,
) -> IntegratedPlacementResult:
    """Minimize sensor cost while closing all specified target variables."""

    config = config or TearingConfig()
    constants = set(known_constants or set())
    costs = dict(sensor_costs or {})
    original_equations = {name: list(values) for name, values in equations.items()}
    variables = all_variables(original_equations)
    variable_set = set(variables)

    for label, values in (
        ("base_measured", base_measured),
        ("known_constants", constants),
        ("candidates", candidates),
        ("targets", targets),
    ):
        unknown = set(values) - variable_set
        if unknown:
            raise ValueError(f"{label} contains unknown variables: {sorted(unknown)}")
    if base_measured & constants:
        raise ValueError("Measured variables and constants must be disjoint")
    overlap = candidates & (base_measured | constants)
    if overlap:
        raise ValueError(f"Candidates already initially known: {sorted(overlap)}")
    if not targets:
        raise ValueError("At least one target variable is required")
    for variable in candidates:
        cost = costs.get(variable, 1)
        if not isinstance(cost, int) or isinstance(cost, bool) or cost <= 0:
            raise ValueError(f"Sensor cost must be a positive integer: {variable}")

    if config.use_structural_preprocessing:
        model_equations, removed, _rank = preprocess_equations_structural(
            original_equations,
            variables,
            use_union_of_maximum_matchings=config.use_union_of_maximum_matchings,
        )
    else:
        model_equations = dict(original_equations)
        removed = []

    uses = {
        variable: [
            name
            for name, values in model_equations.items()
            if variable in values
        ]
        for variable in variables
    }
    permitted: Dict[str, Set[str]] = {}
    for name, values in model_equations.items():
        if allowed_outputs is None:
            permitted[name] = set(values)
        else:
            permitted[name] = set(allowed_outputs.get(name, set(values)))
        invalid = permitted[name] - set(values)
        if invalid:
            raise ValueError(f"Invalid allowed outputs for {name}: {sorted(invalid)}")

    model = cp_model.CpModel()
    sensor = {
        variable: model.NewBoolVar(f"sensor_{variable}")
        for variable in sorted(candidates)
    }
    initial = {}
    for variable in variables:
        if variable in base_measured or variable in constants:
            initial[variable] = model.NewConstant(1)
        elif variable in sensor:
            initial[variable] = sensor[variable]
        else:
            initial[variable] = model.NewConstant(0)

    output = {
        (name, variable): model.NewBoolVar(f"output_{name}_{variable}")
        for name, values in model_equations.items()
        for variable in values
    }
    tear = {
        (name, variable): model.NewBoolVar(f"tear_{name}_{variable}")
        for name, values in model_equations.items()
        for variable in values
    }
    available = {
        variable: model.NewBoolVar(f"available_{variable}")
        for variable in variables
    }
    open_tear = {
        variable: model.NewBoolVar(f"open_tear_{variable}")
        for variable in variables
    }
    external = {
        variable: model.NewBoolVar(f"external_{variable}")
        for variable in variables
    }
    autonomous = {
        variable: model.NewBoolVar(f"autonomous_{variable}")
        for variable in variables
    }
    level = {
        variable: model.NewIntVar(0, len(variables), f"level_{variable}")
        for variable in variables
    }
    direct_pair = {
        (name, variable): model.NewBoolVar(f"direct_{name}_{variable}")
        for name, values in model_equations.items()
        for variable in values
    }

    for variable in variables:
        output_sum = sum(output[name, variable] for name in uses[variable])
        tear_sum = sum(tear[name, variable] for name in uses[variable])
        model.Add(output_sum <= 1)
        model.Add(tear_sum <= 1)
        model.Add(output_sum <= 1 - initial[variable])
        model.Add(tear_sum <= 1 - initial[variable])

        model.Add(available[variable] >= initial[variable])
        model.Add(available[variable] >= output_sum)
        model.Add(available[variable] <= initial[variable] + output_sum)

        model.Add(open_tear[variable] <= tear_sum)
        model.Add(open_tear[variable] <= 1 - output_sum)
        model.Add(open_tear[variable] >= tear_sum - output_sum)
        model.Add(external[variable] >= open_tear[variable])
        model.Add(external[variable] <= 1 - initial[variable])

        model.Add(autonomous[variable] <= available[variable])
        model.Add(autonomous[variable] <= 1 - external[variable])
        model.Add(
            autonomous[variable]
            >= available[variable] - external[variable]
        )

    for name, values in model_equations.items():
        model.Add(sum(output[name, variable] for variable in values) <= 1)
        for variable in values:
            if variable not in permitted[name]:
                model.Add(output[name, variable] == 0)
            model.Add(output[name, variable] + tear[name, variable] <= 1)
            model.Add(
                tear[name, variable]
                <= sum(
                    output[name, other]
                    for other in values
                    if other != variable
                )
            )
            predecessor_tears = [
                tear[name, other]
                for other in values
                if other != variable
            ]
            model.Add(direct_pair[name, variable] <= output[name, variable])
            for predecessor in values:
                if predecessor == variable:
                    continue
                model.Add(
                    output[name, variable]
                    <= available[predecessor] + tear[name, predecessor]
                )
                model.Add(
                    level[variable] >= level[predecessor] + 1
                ).OnlyEnforceIf(
                    [output[name, variable], tear[name, predecessor].Not()]
                )
                model.Add(
                    external[variable]
                    >= external[predecessor] + output[name, variable] - 1
                )
                model.Add(
                    direct_pair[name, variable]
                    <= 1 - tear[name, predecessor]
                )
            if predecessor_tears:
                model.Add(
                    direct_pair[name, variable]
                    >= output[name, variable] - sum(predecessor_tears)
                )
            else:
                model.Add(direct_pair[name, variable] == output[name, variable])

    for variable in targets:
        model.Add(autonomous[variable] == 1)
    if config.max_tears is not None:
        model.Add(sum(tear.values()) <= config.max_tears)

    sensor_cost_expr = sum(
        costs.get(variable, 1) * decision
        for variable, decision in sensor.items()
    )
    closed_expr = sum(autonomous.values())
    external_expr = sum(available.values())
    open_expr = sum(open_tear.values())
    raw_tear_expr = sum(tear.values())
    direct_expr = sum(direct_pair.values())
    phases: List[Tuple[str, str, cp_model.LinearExpr]] = [
        ("phase_1_min_sensor_cost", "min", sensor_cost_expr),
        ("phase_2_max_closed_coverage", "max", closed_expr),
        ("phase_3_max_external_reach", "max", external_expr),
        ("phase_4_min_open_tears", "min", open_expr),
        ("phase_5_min_raw_tears", "min", raw_tear_expr),
        ("phase_6_max_local_direct", "max", direct_expr),
    ]

    statuses: Dict[str, str] = {}
    objectives: Dict[str, float] = {}
    times: Dict[str, float] = {}
    snapshot: Optional[_PlacementSnapshot] = None
    primary_status = "UNKNOWN"
    for index, (phase_name, sense, expression) in enumerate(phases):
        if sense == "min":
            model.Minimize(expression)
        else:
            model.Maximize(expression)
        current_solver = _solver(config)
        status_code = current_solver.Solve(model)
        status_name = current_solver.StatusName(status_code)
        statuses[phase_name] = status_name
        times[phase_name] = current_solver.WallTime()
        if status_code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            break
        value = int(round(current_solver.ObjectiveValue()))
        objectives[phase_name] = current_solver.ObjectiveValue()
        if index == 0:
            primary_status = status_name
        selected = tuple(
            sorted(
                variable
                for variable, decision in sensor.items()
                if current_solver.Value(decision)
            )
        )
        snapshot = _PlacementSnapshot(
            selected=selected,
            selected_cost=sum(costs.get(variable, 1) for variable in selected),
            target_covered=all(
                current_solver.Value(autonomous[variable])
                for variable in targets
            ),
            n_closed=sum(
                current_solver.Value(decision)
                for decision in autonomous.values()
            ),
            n_external=sum(
                current_solver.Value(decision)
                for decision in available.values()
            ),
            n_open=sum(
                current_solver.Value(decision)
                for decision in open_tear.values()
            ),
            n_raw=sum(
                current_solver.Value(decision)
                for decision in tear.values()
            ),
        )
        if index < len(phases) - 1:
            model.Add(expression == value)

    if snapshot is None:
        return IntegratedPlacementResult(
            case_name=case_name,
            selected_sensors=(),
            selected_cost=0,
            minimum_certified=False,
            target_variables=tuple(sorted(targets)),
            target_covered=False,
            n_closed_coverage=0,
            n_external_reach=0,
            n_open_tears=0,
            n_raw_tears=0,
            status_by_phase=statuses,
            objective_by_phase=objectives,
            time_by_phase_s=times,
            retained_equations=tuple(model_equations),
            removed_equations=tuple(removed),
        )

    return IntegratedPlacementResult(
        case_name=case_name,
        selected_sensors=snapshot.selected,
        selected_cost=snapshot.selected_cost,
        minimum_certified=primary_status == "OPTIMAL",
        target_variables=tuple(sorted(targets)),
        target_covered=snapshot.target_covered,
        n_closed_coverage=snapshot.n_closed,
        n_external_reach=snapshot.n_external,
        n_open_tears=snapshot.n_open,
        n_raw_tears=snapshot.n_raw,
        status_by_phase=statuses,
        objective_by_phase=objectives,
        time_by_phase_s=times,
        retained_equations=tuple(model_equations),
        removed_equations=tuple(removed),
    )

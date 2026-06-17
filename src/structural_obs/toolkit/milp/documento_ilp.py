#!/usr/bin/env python3
"""URS document MILP sensor placement (y/z model).

Migrated from codes_URS/CODIGO_VALIDADO/URS_ILP_documento_ideal.py.
Semantics differ from CP-SAT tearing min_repair; see planning.md section 6.3.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Sequence, Set, Tuple

from ortools.linear_solver import pywraplp

from structural_obs.toolkit.milp.sensor_groups import SensorGroups, sensor_groups_urs_document

Equations = Dict[str, List[str]]
MilpMode = Literal["global", "repair", "verify"]
MilpStatus = Literal["optimal", "feasible", "infeasible", "not_optimal", "error"]


@dataclass(frozen=True)
class MilpPlacementResult:
    """Auditable MILP placement solution."""

    mode: MilpMode
    status: MilpStatus
    status_code: int
    solver_name: str
    measured: Tuple[str, ...]
    inferred: Tuple[str, ...]
    sensor_count: int
    redundancy_cost: float
    base_measured: Tuple[str, ...]
    additions: Tuple[str, ...]
    y_values: Dict[str, float]
    z_values: Dict[str, float]


def all_variables(equations: Equations) -> List[str]:
    """Sorted union of variables in equations."""
    universe: Set[str] = set()
    for variables in equations.values():
        universe.update(variables)
    return sorted(universe)


def _make_solver() -> Tuple[pywraplp.Solver, str]:
    for name in ("SCIP", "CBC"):
        solver = pywraplp.Solver.CreateSolver(name)
        if solver is not None:
            return solver, name
    raise RuntimeError("No OR-Tools MILP solver available (tried SCIP, CBC).")


def _setup_model(
    solver: pywraplp.Solver, flows: Sequence[str]
) -> Tuple[Dict[str, pywraplp.Variable], Dict[str, pywraplp.Variable]]:
    y_vars = {name: solver.IntVar(0, 1, f"y_{name}") for name in flows}
    z_vars = {name: solver.IntVar(0, 1, f"z_{name}") for name in flows}
    return y_vars, z_vars


def _add_constraints_full(
    solver: pywraplp.Solver,
    y: Dict[str, pywraplp.Variable],
    z: Dict[str, pywraplp.Variable],
    flows: Sequence[str],
    equations: Equations,
    sensor_groups: SensorGroups,
) -> None:
    for name in flows:
        solver.Add(y[name] + z[name] == 1)

    solver.Add(y["F"] + y["R"] >= 1)
    solver.Add(solver.Sum(y[v] for v in sensor_groups["permeados"]) >= 2)

    for _eq_name, eq_vars in equations.items():
        n_sensors = solver.Sum(y[v] for v in eq_vars)
        solver.Add(n_sensors >= 1)
        solver.Add(n_sensors <= 3)
        for var in eq_vars:
            others = [v for v in eq_vars if v != var]
            solver.Add(z[var] <= solver.Sum(y[v] for v in others))


def _fix_measured_pattern(
    solver: pywraplp.Solver,
    y: Dict[str, pywraplp.Variable],
    z: Dict[str, pywraplp.Variable],
    flows: Sequence[str],
    measured: Set[str],
) -> None:
    unknown = measured - set(flows)
    if unknown:
        raise ValueError(f"Measured set has unknown variables: {sorted(unknown)}")
    for name in flows:
        if name in measured:
            solver.Add(y[name] == 1)
            solver.Add(z[name] == 0)
        else:
            solver.Add(y[name] == 0)
            solver.Add(z[name] == 1)


def _apply_repair_bounds(
    solver: pywraplp.Solver,
    y: Dict[str, pywraplp.Variable],
    flows: Sequence[str],
    base_measured: Set[str],
    candidates: Set[str],
) -> None:
    unknown_base = base_measured - set(flows)
    if unknown_base:
        raise ValueError(f"base_measured unknown vars: {sorted(unknown_base)}")
    unknown_cand = candidates - set(flows)
    if unknown_cand:
        raise ValueError(f"candidates unknown vars: {sorted(unknown_cand)}")
    allowed_new = candidates - base_measured
    for name in flows:
        if name in base_measured:
            solver.Add(y[name] == 1)
        elif name in allowed_new:
            continue
        else:
            solver.Add(y[name] == 0)


def _redundancy_cost(y_sol: Dict[str, float], equations: Equations) -> float:
    total = 0.0
    for _eq, eq_vars in equations.items():
        sensors = [v for v in eq_vars if y_sol[v] > 0.5]
        if len(sensors) >= 2:
            total += float(len(sensors) - 2)
    return total


def _decode_solution(
    y: Dict[str, pywraplp.Variable],
    z: Dict[str, pywraplp.Variable],
    flows: Sequence[str],
) -> Tuple[Dict[str, float], Dict[str, float]]:
    y_sol = {name: y[name].solution_value() for name in flows}
    z_sol = {name: z[name].solution_value() for name in flows}
    return y_sol, z_sol


def _status_label(code: int) -> MilpStatus:
    if code == pywraplp.Solver.OPTIMAL:
        return "optimal"
    if code == pywraplp.Solver.FEASIBLE:
        return "feasible"
    return "infeasible"


def solve_milp_placement(
    equations: Equations,
    mode: MilpMode,
    *,
    sensor_groups: Optional[SensorGroups] = None,
    base_measured: Optional[Set[str]] = None,
    candidates: Optional[Set[str]] = None,
    fixed_measured: Optional[Set[str]] = None,
) -> MilpPlacementResult:
    """Run URS document MILP placement for global, repair, or verify mode."""
    groups = sensor_groups or sensor_groups_urs_document()
    flows = all_variables(equations)
    base = frozenset(base_measured or set())
    cand = frozenset(candidates or set())

    solver, solver_name = _make_solver()
    y, z = _setup_model(solver, flows)
    _add_constraints_full(solver, y, z, flows, equations, groups)

    if mode == "global":
        solver.Minimize(solver.Sum(y[v] for v in flows))
    elif mode == "repair":
        if not base:
            raise ValueError("milp_repair requires non-empty base_measured")
        _apply_repair_bounds(solver, y, flows, set(base), cand)
        solver.Minimize(solver.Sum(y[v] for v in flows))
    elif mode == "verify":
        fixed = fixed_measured if fixed_measured is not None else set(base)
        if not fixed:
            raise ValueError("milp_verify requires fixed measured set")
        _fix_measured_pattern(solver, y, z, flows, set(fixed))
        solver.Minimize(0)
    else:
        raise ValueError(f"Unknown MILP mode: {mode}")

    status_code = solver.Solve()
    if mode == "verify":
        ok = status_code in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE)
        label: MilpStatus = "feasible" if ok else "infeasible"
        if not ok:
            return MilpPlacementResult(
                mode=mode,
                status=label,
                status_code=status_code,
                solver_name=solver_name,
                measured=tuple(),
                inferred=tuple(),
                sensor_count=0,
                redundancy_cost=0.0,
                base_measured=tuple(sorted(fixed)),
                additions=tuple(),
                y_values={},
                z_values={},
            )
    else:
        if status_code != pywraplp.Solver.OPTIMAL:
            if status_code == pywraplp.Solver.INFEASIBLE:
                failed_label: MilpStatus = "infeasible"
            else:
                failed_label = "not_optimal"
            return MilpPlacementResult(
                mode=mode,
                status=failed_label,
                status_code=status_code,
                solver_name=solver_name,
                measured=tuple(),
                inferred=tuple(),
                sensor_count=0,
                redundancy_cost=0.0,
                base_measured=tuple(sorted(base)),
                additions=tuple(),
                y_values={},
                z_values={},
            )
        label = "optimal"

    y_sol, z_sol = _decode_solution(y, z, flows)
    measured = tuple(sorted(v for v in flows if y_sol[v] > 0.5))
    inferred = tuple(sorted(v for v in flows if z_sol[v] > 0.5))
    additions = tuple(sorted(set(measured) - set(base)))
    return MilpPlacementResult(
        mode=mode,
        status=label,
        status_code=status_code,
        solver_name=solver_name,
        measured=measured,
        inferred=inferred,
        sensor_count=len(measured),
        redundancy_cost=_redundancy_cost(y_sol, equations),
        base_measured=tuple(sorted(base)),
        additions=additions,
        y_values=y_sol,
        z_values=z_sol,
    )


def explain_milp_conflicts(
    equations: Equations,
    measured: Set[str],
    sensor_groups: Optional[SensorGroups] = None,
) -> List[str]:
    """Text-only MILP rule checks (no solver). Returns user-facing messages in PT-BR."""
    groups = sensor_groups or sensor_groups_urs_document()
    flows = set(all_variables(equations))
    issues: List[str] = []
    unknown = measured - flows
    if unknown:
        issues.append(f"Grandezas desconhecidas no conjunto medido: {sorted(unknown)}")
    inferred = flows - measured

    if (1 if "F" in measured else 0) + (1 if "R" in measured else 0) < 1:
        issues.append("Regra F+R: é necessário medir pelo menos uma entre F e R.")

    n_perm = sum(1 for v in groups["permeados"] if v in measured)
    if n_perm < 2:
        issues.append(
            f"Regra permeados: são necessários pelo menos 2 entre PA..PE; "
            f"encontrados {n_perm}."
        )

    for eq_name, eq_vars in sorted(equations.items()):
        ys = [v for v in eq_vars if v in measured]
        if len(ys) < 1:
            issues.append(f"Regra por equação: {eq_name} não tem variáveis medidas.")
        if len(ys) > 3:
            issues.append(
                f"Regra por equação: {eq_name} tem {len(ys)} medidas (máximo 3)."
            )

    for var in sorted(inferred):
        for eq_name, eq_vars in equations.items():
            if var not in eq_vars:
                continue
            others = [u for u in eq_vars if u != var and u in measured]
            if not others:
                issues.append(
                    f"Regra suporte de z: {var} inferida em {eq_name} precisa de "
                    f"outra medida na mesma equação."
                )
    return issues

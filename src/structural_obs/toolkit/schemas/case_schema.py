#!/usr/bin/env python3
"""Case definition schema (v1.0) for YAML-driven analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Mapping, Optional, Set

Equations = Dict[str, List[str]]
Objective = Literal["classify", "min_repair"]
Criterion = Literal["C_cl", "C_ext"]

_VAR_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SUPPORTED_SCHEMA_VERSIONS = frozenset({"1.0"})


@dataclass(frozen=True)
class SolverConfig:
    """CP-SAT tearing solver options."""

    time_limit_s: float = 60.0
    require_optimal: bool = True
    use_structural_preprocessing: bool = True
    random_seed: int = 42


@dataclass(frozen=True)
class InstrumentationConfig:
    """Measured sensors and known physical parameters."""

    measured: frozenset[str] = frozenset()
    known_constants: frozenset[str] = frozenset()


@dataclass(frozen=True)
class RepairConfig:
    """Minimum repair search configuration."""

    base_measured: frozenset[str]
    candidates: tuple[str, ...]
    candidate_pool: str = "failed"
    max_additions: Optional[int] = None


@dataclass(frozen=True)
class AnalysisConfig:
    """Analysis objective and feasibility criterion."""

    objective: Objective
    criterion: Criterion = "C_cl"
    repair: Optional[RepairConfig] = None


@dataclass(frozen=True)
class CaseDefinition:
    """Validated case ready for execution."""

    schema_version: str
    case_id: str
    name: str
    section: str
    equations: Equations
    instrumentation: InstrumentationConfig
    allowed_outputs: Optional[Mapping[str, frozenset[str]]] = None
    analysis: AnalysisConfig = field(
        default_factory=lambda: AnalysisConfig(objective="classify")
    )
    solver: SolverConfig = field(default_factory=SolverConfig)
    equations_profile: Optional[str] = None
    source_path: Optional[str] = None

    @property
    def all_variables(self) -> Set[str]:
        variables: Set[str] = set()
        for eq_vars in self.equations.values():
            variables.update(eq_vars)
        return variables


@dataclass(frozen=True)
class CaseDocument:
    """Raw document wrapper before equation resolution."""

    schema_version: str
    case_id: str
    name: str
    section: str
    equations: Optional[Equations]
    equations_profile: Optional[str]
    instrumentation: InstrumentationConfig
    allowed_outputs: Optional[Mapping[str, frozenset[str]]]
    analysis: AnalysisConfig
    solver: SolverConfig
    source_path: Optional[str] = None


def _validate_variable_name(name: str, context: str) -> None:
    if not _VAR_PATTERN.match(name):
        raise ValueError(f"Invalid ASCII variable name '{name}' in {context}")


def _validate_equations(equations: Equations) -> None:
    if not equations:
        raise ValueError("Case must define at least one equation")
    for eq_name, variables in equations.items():
        _validate_variable_name(eq_name, f"equation key '{eq_name}'")
        if len(variables) < 2:
            raise ValueError(f"Equation '{eq_name}' must list at least two variables")
        for var in variables:
            _validate_variable_name(var, f"equation '{eq_name}'")


def _validate_subset(values: Set[str], universe: Set[str], label: str) -> None:
    unknown = values - universe
    if unknown:
        raise ValueError(f"{label} references unknown variables: {sorted(unknown)}")


def validate_case_document(doc: CaseDocument, equations: Equations) -> CaseDefinition:
    """Validate a resolved case document and return a CaseDefinition."""
    if doc.schema_version not in _SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(
            f"Unsupported schema_version '{doc.schema_version}'. "
            f"Supported: {sorted(_SUPPORTED_SCHEMA_VERSIONS)}"
        )
    _validate_equations(equations)
    universe = {v for vs in equations.values() for v in vs}

    measured = set(doc.instrumentation.measured)
    constants = set(doc.instrumentation.known_constants)
    overlap = measured & constants
    if overlap:
        raise ValueError(f"Variables cannot be both measured and known_constants: {sorted(overlap)}")

    _validate_subset(measured, universe, "measured")
    _validate_subset(constants, universe, "known_constants")

    if doc.allowed_outputs:
        for eq_name, allowed in doc.allowed_outputs.items():
            if eq_name not in equations:
                raise ValueError(f"allowed_outputs references unknown equation '{eq_name}'")
            _validate_subset(set(allowed), set(equations[eq_name]), f"allowed_outputs[{eq_name}]")

    if doc.analysis.objective == "min_repair":
        if doc.analysis.repair is None:
            raise ValueError("min_repair objective requires analysis.repair section")
        base = set(doc.analysis.repair.base_measured)
        _validate_subset(base, universe, "repair.base_measured")
        for cand in doc.analysis.repair.candidates:
            _validate_variable_name(cand, "repair.candidates")
        if doc.analysis.criterion != "C_cl":
            raise ValueError("min_repair currently supports criterion C_cl only")

    return CaseDefinition(
        schema_version=doc.schema_version,
        case_id=doc.case_id,
        name=doc.name,
        section=doc.section,
        equations=dict(equations),
        instrumentation=doc.instrumentation,
        allowed_outputs=doc.allowed_outputs,
        analysis=doc.analysis,
        solver=doc.solver,
        equations_profile=doc.equations_profile,
        source_path=doc.source_path,
    )

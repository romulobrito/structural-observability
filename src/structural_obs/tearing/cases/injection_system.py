#!/usr/bin/env python3
"""Adapters for the complete and reduced water injection system inputs."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Mapping, Set

from structural_obs.tearing.cases.system_model import (
    StructuralSystemData,
    register_source,
)

Equations = Dict[str, List[str]]
BlockRanges = tuple[tuple[str, int, int], ...]
DuplicateDeclarations = tuple[tuple[str, tuple[str, ...]], ...]


InjectionSystemData = StructuralSystemData


BLOCK_RANGES: BlockRanges = (
    ("urs_balances", 73, 92),
    ("stage_kpis", 93, 122),
    ("bank_kpis", 123, 167),
    ("booster", 68, 72),
    ("fine_filters", 63, 67),
    ("coarse_filters", 58, 62),
    ("biocide", 168, 171),
    ("antiscalant", 172, 174),
    ("bisulfite", 175, 178),
    ("cleaning", 179, 192),
    ("deaeration", 193, 197),
    ("water_distribution", 27, 28),
    ("distribution_filters", 29, 34),
    ("heat_exchangers", 35, 40),
    ("cooling_water_ac", 41, 49),
    ("cooling_water_anc", 50, 57),
    ("injection_pumping", 198, 207),
    ("hypochlorite_injection", 14, 26),
    ("electrochlorination", 1, 10),
    ("hypochlorite_tank", 11, 13),
)

KNOWN_CONSTANTS = frozenset({"A", "Lp", "Dpi"})

REDUCED_BLOCK_RANGES: BlockRanges = (
    ("urs_balances", 69, 88),
    ("stage_kpis", 89, 118),
    ("bank_kpis", 119, 163),
    ("booster", 64, 68),
    ("fine_filters", 59, 63),
    ("coarse_filters", 54, 58),
    ("biocide", 164, 167),
    ("antiscalant", 168, 170),
    ("bisulfite", 171, 174),
    ("cleaning", 175, 188),
    ("deaeration", 189, 193),
    ("water_distribution", 23, 24),
    ("distribution_filters", 25, 30),
    ("heat_exchangers", 31, 36),
    ("cooling_water_ac", 37, 45),
    ("cooling_water_anc", 46, 53),
    ("injection_pumping", 194, 203),
    ("hypochlorite_injection", 12, 22),
    ("electrochlorination", 1, 9),
    ("hypochlorite_tank", 10, 11),
)


@dataclass(frozen=True)
class _InjectionSourceSpec:
    """Metadata that distinguishes one injection-system input file."""

    profile: str
    filename: str
    block_ranges: BlockRanges


_COMPLETE_SPEC = _InjectionSourceSpec(
    profile="injection_system",
    filename="novo_equacoes_injecao.py",
    block_ranges=BLOCK_RANGES,
)
_REDUCED_SPEC = _InjectionSourceSpec(
    profile="injection_system_no_ob_dr",
    filename="equacoes_inejecao_sem_OB_DR.py",
    block_ranges=REDUCED_BLOCK_RANGES,
)


def _source_path(filename: str) -> Path:
    project_root = Path(__file__).resolve().parents[4]
    return project_root / "sistema-comleto-inj-agua-urs" / filename


def _load_source_module(path: Path) -> ModuleType:
    if not path.is_file():
        raise FileNotFoundError(f"Injection system source not found: {path}")
    module_name = "injection_source_{0}".format(path.stem)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load injection system source: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _equation_number(name: str) -> int:
    """Return the numeric identity of an EqN name."""

    suffix = name[2:]
    if not name.startswith("Eq") or not suffix.isdigit():
        raise ValueError(
            "Equation name has no numeric identity: {0}".format(name)
        )
    return int(suffix)


def _duplicate_groups(equations: Equations) -> tuple[tuple[str, ...], ...]:
    """Group equations that list the same variables, ordered by number."""

    signatures: Dict[tuple[str, ...], List[str]] = {}
    for name, variables in equations.items():
        signature = tuple(sorted(variables))
        signatures.setdefault(signature, []).append(name)
    groups = [
        tuple(sorted(names, key=_equation_number))
        for names in signatures.values()
        if len(names) > 1
    ]
    groups.sort(key=lambda names: _equation_number(names[0]))
    return tuple(groups)


def _duplicates_from_groups(
    groups: tuple[tuple[str, ...], ...],
) -> DuplicateDeclarations:
    """Keep the lowest equation number and mark the other copies."""

    return tuple((names[0], names[1:]) for names in groups)


def _blocks_from_ranges(
    equations: Equations,
    block_ranges: BlockRanges,
) -> Dict[str, tuple[str, ...]]:
    """Assign every equation to exactly one declared block."""

    blocks: Dict[str, tuple[str, ...]] = {}
    seen: Dict[str, str] = {}
    for block_id, start, end in block_ranges:
        if block_id in blocks:
            raise ValueError(f"Duplicate block id: {block_id}")
        if end < start:
            raise ValueError(f"Invalid range for block {block_id}")
        names: List[str] = []
        for number in range(start, end + 1):
            name = f"Eq{number}"
            if name not in equations:
                raise ValueError(f"Missing equation {name} in block {block_id}")
            owner = seen.get(name)
            if owner is not None:
                raise ValueError(
                    f"Equation {name} belongs to {owner} and {block_id}"
                )
            seen[name] = block_id
            names.append(name)
        blocks[block_id] = tuple(names)
    missing = sorted(set(equations) - set(seen))
    if missing:
        raise ValueError(
            "Equations outside block ranges: {0}".format(", ".join(missing))
        )
    return blocks


def _load_injection_source(spec: _InjectionSourceSpec) -> InjectionSystemData:
    """Load one injection input without changing the shared validation rules."""

    module = _load_source_module(_source_path(spec.filename))
    factory = getattr(module, "equacoes_injecao", None)
    if not callable(factory):
        raise AttributeError("Source must define callable equacoes_injecao")
    payload = factory()
    if not isinstance(payload, tuple) or len(payload) != 5:
        raise ValueError("equacoes_injecao must return five values")
    equations_raw, variables_raw, _weights, sensors_raw, outputs_raw = payload
    if not isinstance(equations_raw, dict):
        raise TypeError("Injection equations must be a dictionary")

    equations: Equations = {}
    for name, values in equations_raw.items():
        if not isinstance(name, str) or not isinstance(values, list):
            raise TypeError("Invalid equation entry in injection source")
        if len(values) < 2 or not all(isinstance(value, str) for value in values):
            raise ValueError(f"Invalid variables in equation {name}")
        equations[name] = list(values)

    variables = tuple(
        sorted({value for values in equations.values() for value in values})
    )
    if set(variables_raw) != set(variables):
        raise ValueError("Declared variables differ from equation variables")
    sensors = frozenset(str(value) for value in sensors_raw)
    outputs = frozenset(str(value) for value in outputs_raw)
    unknown_sensors = sensors - set(variables)
    unknown_outputs = outputs - set(variables)
    if unknown_sensors:
        raise ValueError(f"Unknown installed sensors: {sorted(unknown_sensors)}")
    if unknown_outputs:
        raise ValueError(f"Unknown calculated outputs: {sorted(unknown_outputs)}")
    constants = KNOWN_CONSTANTS & sensors
    measured = sensors - constants
    blocks = _blocks_from_ranges(equations, spec.block_ranges)
    kpi_equations = set(blocks["stage_kpis"]) | set(blocks["bank_kpis"])
    allowed_outputs = {
        name: frozenset({values[0]})
        for name, values in equations.items()
        if name in kpi_equations
    }
    duplicate_groups = _duplicate_groups(equations)
    return InjectionSystemData(
        profile=spec.profile,
        equations=equations,
        variables=variables,
        installed_sensors=frozenset(measured),
        known_constants=frozenset(constants),
        calculated_outputs=outputs,
        blocks=blocks,
        allowed_outputs=allowed_outputs,
        duplicate_equation_groups=duplicate_groups,
        declared_duplicates=_duplicates_from_groups(duplicate_groups),
    )


def load_injection_system() -> InjectionSystemData:
    """Load and validate the existing complete-system Python input."""

    return _load_injection_source(_COMPLETE_SPEC)


def load_injection_system_no_ob_dr() -> InjectionSystemData:
    """Load the reduced input that drops overboard, drain, and open-drain terms."""

    return _load_injection_source(_REDUCED_SPEC)


def equations_for_range(
    equations: Equations,
    start: int,
    end: int,
) -> Equations:
    """Return an inclusive equation-number range."""

    selected: Equations = {}
    for number in range(start, end + 1):
        name = f"Eq{number}"
        if name not in equations:
            raise KeyError(f"Missing equation {name}")
        selected[name] = list(equations[name])
    return selected


def default_allowed_outputs(
    equations: Equations,
    declared: Mapping[str, frozenset[str]] | None = None,
) -> Dict[str, Set[str]]:
    """Restrict equations to outputs declared by source metadata."""

    metadata = declared
    if metadata is None:
        metadata = load_injection_system().allowed_outputs
    return {
        name: set(metadata[name])
        for name in equations
        if name in metadata
    }


register_source("injection_system", load_injection_system)
register_source("injection_system_no_ob_dr", load_injection_system_no_ob_dr)

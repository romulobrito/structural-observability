#!/usr/bin/env python3
"""Generic structural-system input contract and source registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping

Equations = Dict[str, List[str]]
DuplicateDeclaration = tuple[str, tuple[str, ...]]


@dataclass(frozen=True)
class StructuralSystemData:
    """Normalized metadata required by a structural campaign."""

    profile: str
    equations: Equations
    variables: tuple[str, ...]
    installed_sensors: frozenset[str]
    known_constants: frozenset[str]
    calculated_outputs: frozenset[str]
    blocks: Mapping[str, tuple[str, ...]]
    allowed_outputs: Mapping[str, frozenset[str]]
    duplicate_equation_groups: tuple[tuple[str, ...], ...]
    declared_duplicates: tuple[DuplicateDeclaration, ...] = ()


SourceLoader = Callable[[], StructuralSystemData]
_LOADERS: dict[str, SourceLoader] = {}


def register_source(profile: str, loader: SourceLoader) -> None:
    """Register one profile loader without embedding domain rules in the engine."""

    normalized = profile.strip()
    if not normalized:
        raise ValueError("Source profile must not be empty")
    if normalized in _LOADERS and _LOADERS[normalized] is not loader:
        raise ValueError(f"Source profile already registered: {normalized}")
    _LOADERS[normalized] = loader


def load_source(profile: str) -> StructuralSystemData:
    """Load a registered structural-system profile."""

    loader = _LOADERS.get(profile)
    if loader is None:
        raise ValueError(f"Unknown source profile: {profile}")
    return loader()


def normalize_declared_duplicates(
    source: StructuralSystemData,
) -> tuple[Equations, tuple[str, ...]]:
    """Remove only duplicates explicitly declared by the source adapter."""

    equations = {name: list(values) for name, values in source.equations.items()}
    removed: list[str] = []
    for canonical, duplicates in source.declared_duplicates:
        if canonical not in equations:
            raise ValueError(f"Missing canonical equation: {canonical}")
        canonical_signature = tuple(sorted(equations[canonical]))
        for duplicate in duplicates:
            if duplicate not in equations:
                raise ValueError(f"Missing declared duplicate equation: {duplicate}")
            if tuple(sorted(equations[duplicate])) != canonical_signature:
                raise ValueError(
                    f"Declared duplicate incidence differs: {canonical}, {duplicate}"
                )
            del equations[duplicate]
            removed.append(duplicate)
    return equations, tuple(sorted(removed))


def select_block_equations(
    source: StructuralSystemData,
    block_id: str,
    equations: Mapping[str, List[str]],
) -> Equations:
    """Select one semantic block from a possibly normalized equation map."""

    names = source.blocks.get(block_id)
    if names is None:
        raise ValueError(f"Unknown equation block: {block_id}")
    return {
        name: list(equations[name])
        for name in names
        if name in equations
    }

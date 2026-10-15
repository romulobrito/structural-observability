"""Benchmark case equation definitions and registered source profiles."""

from structural_obs.tearing.cases import injection_system as injection_system
from structural_obs.tearing.cases.system_model import (
    StructuralSystemData,
    load_source,
    normalize_declared_duplicates,
    register_source,
    select_block_equations,
)

__all__ = [
    "StructuralSystemData",
    "injection_system",
    "load_source",
    "normalize_declared_duplicates",
    "register_source",
    "select_block_equations",
]

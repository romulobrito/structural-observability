"""CP-SAT tearing classification engine (migrated from cp-sat-tearing-public)."""

from structural_obs.tearing.core import (
    TearingConfig,
    TearingResult,
    all_variables,
    classify_tearing,
    preprocess_equations_structural,
    validate_result,
)

__all__ = [
    "TearingConfig",
    "TearingResult",
    "all_variables",
    "classify_tearing",
    "preprocess_equations_structural",
    "validate_result",
]

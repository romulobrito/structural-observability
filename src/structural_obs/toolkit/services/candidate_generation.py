#!/usr/bin/env python3
"""Generate auditable sensor candidates after structural classification."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Set

import yaml

from structural_obs.tearing.core import TearingResult

Equations = Dict[str, List[str]]


@dataclass(frozen=True)
class CandidateSuggestion:
    """One automatically generated sensor candidate."""

    variable: str
    reasons: tuple[str, ...]
    distance_to_uncovered_target: int
    approved: bool = False


def _variable_adjacency(equations: Mapping[str, Sequence[str]]) -> Dict[str, Set[str]]:
    adjacency: Dict[str, Set[str]] = {}
    for variables in equations.values():
        unique = set(variables)
        for variable in unique:
            adjacency.setdefault(variable, set()).update(unique - {variable})
    return adjacency


def _distances(
    adjacency: Mapping[str, Set[str]],
    sources: Set[str],
    max_depth: int,
) -> Dict[str, int]:
    distances = {source: 0 for source in sources}
    queue = deque(sorted(sources))
    while queue:
        current = queue.popleft()
        depth = distances[current]
        if depth >= max_depth:
            continue
        for neighbor in sorted(adjacency.get(current, set())):
            if neighbor not in distances:
                distances[neighbor] = depth + 1
                queue.append(neighbor)
    return distances


def generate_sensor_candidates(
    equations: Mapping[str, Sequence[str]],
    result: TearingResult,
    targets: Iterable[str],
    *,
    calculated_outputs: Iterable[str] = (),
    prohibited: Iterable[str] = (),
    max_dependency_depth: int = 2,
) -> tuple[CandidateSuggestion, ...]:
    """Suggest candidates linked to uncovered targets and structural gaps."""

    target_set = set(targets)
    covered = result.closed_coverage_variables
    uncovered = target_set - covered
    if not uncovered:
        return ()

    excluded = (
        set(result.measured)
        | set(result.known_constants)
        | set(calculated_outputs)
        | set(prohibited)
    )
    adjacency = _variable_adjacency(equations)
    distances = _distances(adjacency, uncovered, max_dependency_depth)
    open_tears = set(result.tears_open)
    indeterminate = set(result.effective_indeterminate)

    candidate_variables = (
        open_tears
        | indeterminate
        | set(distances)
    ) - excluded
    suggestions = []
    for variable in sorted(candidate_variables):
        reasons = []
        if variable in open_tears:
            reasons.append("open_tear")
        if variable in indeterminate:
            reasons.append("effective_indeterminate")
        if variable in distances:
            reasons.append("target_dependency")
        suggestions.append(
            CandidateSuggestion(
                variable=variable,
                reasons=tuple(reasons),
                distance_to_uncovered_target=distances.get(
                    variable,
                    max_dependency_depth + 1,
                ),
            )
        )
    return tuple(
        sorted(
            suggestions,
            key=lambda item: (
                item.distance_to_uncovered_target,
                "open_tear" not in item.reasons,
                item.variable,
            ),
        )
    )


def suggestion_entered_tier(item: CandidateSuggestion) -> int:
    """Return the first automatic expansion tier that includes this suggestion."""

    if item.distance_to_uncovered_target <= 1:
        return 1
    if item.distance_to_uncovered_target <= 2:
        return 2
    return 3


def automatic_candidate_tiers(
    suggestions: Sequence[CandidateSuggestion],
) -> tuple[frozenset[str], ...]:
    """Build cumulative automatic tiers near targets before broad expansion."""

    tiers: list[frozenset[str]] = []
    for maximum_distance in (1, 2):
        tier = frozenset(
            item.variable
            for item in suggestions
            if item.distance_to_uncovered_target <= maximum_distance
        )
        if tier and (not tiers or tier != tiers[-1]):
            tiers.append(tier)
    all_candidates = frozenset(item.variable for item in suggestions)
    if all_candidates and (not tiers or all_candidates != tiers[-1]):
        tiers.append(all_candidates)
    return tuple(tiers)


def suggestions_to_yaml(
    campaign_id: str,
    by_stage: Mapping[str, Sequence[CandidateSuggestion]],
) -> str:
    """Serialize candidate suggestions for engineering review."""

    payload = {
        "schema_version": "1.0",
        "campaign_id": campaign_id,
        "stages": {
            stage_id: [asdict(item) for item in suggestions]
            for stage_id, suggestions in by_stage.items()
        },
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)

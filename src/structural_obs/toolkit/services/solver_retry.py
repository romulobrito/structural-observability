#!/usr/bin/env python3
"""Deterministic adaptive retry policy for structural solver calls."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Generic, Mapping, Sequence, TypeVar

from structural_obs.tearing.core import TearingConfig

ResultT = TypeVar("ResultT")


@dataclass(frozen=True)
class SolverAttemptRecord:
    """Audit record for one solver attempt."""

    operation: str
    component_id: str
    attempt: int
    time_limit_s: float
    terminal_status: str
    certified: bool
    error: str = ""


@dataclass(frozen=True)
class RetryOutcome(Generic[ResultT]):
    """Final result and all attempts used to obtain it."""

    result: ResultT
    attempts: tuple[SolverAttemptRecord, ...]


def _global_status(statuses: Mapping[str, str]) -> str:
    values = set(statuses.values())
    if values == {"OPTIMAL"}:
        return "OPTIMAL"
    if "INFEASIBLE" in values:
        return "INFEASIBLE"
    if "UNKNOWN" in values:
        return "UNKNOWN"
    if "FEASIBLE" in values:
        return "FEASIBLE"
    return ",".join(sorted(values)) if values else "UNKNOWN"


def run_with_adaptive_retry(
    *,
    operation: str,
    component_id: str,
    base_config: TearingConfig,
    time_limits_s: Sequence[float],
    runner: Callable[[TearingConfig], ResultT],
    status_getter: Callable[[ResultT], Mapping[str, str]],
    certificate_getter: Callable[[ResultT], bool],
) -> RetryOutcome[ResultT]:
    """Retry uncertified or timed-out calls with increasing time limits."""

    if not time_limits_s:
        raise ValueError("At least one retry time limit is required")
    attempts: list[SolverAttemptRecord] = []
    last_result: ResultT | None = None
    last_error: RuntimeError | None = None
    for attempt_index, time_limit in enumerate(time_limits_s, start=1):
        config = replace(base_config, time_limit_s=float(time_limit))
        try:
            result = runner(config)
        except RuntimeError as error:
            last_error = error
            attempts.append(
                SolverAttemptRecord(
                    operation=operation,
                    component_id=component_id,
                    attempt=attempt_index,
                    time_limit_s=float(time_limit),
                    terminal_status="ERROR",
                    certified=False,
                    error=str(error),
                )
            )
            continue
        last_result = result
        status = _global_status(status_getter(result))
        certified = certificate_getter(result)
        attempts.append(
            SolverAttemptRecord(
                operation=operation,
                component_id=component_id,
                attempt=attempt_index,
                time_limit_s=float(time_limit),
                terminal_status=status,
                certified=certified,
            )
        )
        if certified or status == "INFEASIBLE":
            return RetryOutcome(result=result, attempts=tuple(attempts))
    if last_result is not None:
        return RetryOutcome(result=last_result, attempts=tuple(attempts))
    if last_error is not None:
        raise RuntimeError(
            f"{operation} failed after {len(attempts)} attempts: {last_error}"
        ) from last_error
    raise RuntimeError(f"{operation} produced no result")

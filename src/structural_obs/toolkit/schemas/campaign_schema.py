#!/usr/bin/env python3
"""Schema and loader for additive instrumentation campaigns."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import yaml


@dataclass(frozen=True)
class CampaignSolverConfig:
    """Solver controls shared by all campaign stages."""

    time_limit_s: float = 60.0
    random_seed: int = 42
    use_structural_preprocessing: bool = True
    retry_time_limits_s: tuple[float, ...] = (60.0, 300.0, 600.0)
    decompose_components: bool = True
    max_tears: Optional[int] = None
    num_search_workers: int = 1


@dataclass(frozen=True)
class CampaignStage:
    """One equation block added to the cumulative campaign."""

    stage_id: str
    name: str
    equation_start: Optional[int] = None
    equation_end: Optional[int] = None
    block_id: Optional[str] = None
    targets: tuple[str, ...] = ()
    target_mode: str = "default"
    approved_candidates: tuple[str, ...] = ()
    prohibited_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class CampaignDefinition:
    """Validated additive campaign definition."""

    schema_version: str
    campaign_id: str
    name: str
    source_profile: str
    candidate_mode: str
    default_target_profile: str
    stages: tuple[CampaignStage, ...]
    sensor_costs: Mapping[str, int]
    solver: CampaignSolverConfig
    source_path: str
    normalize_declared_duplicates: bool = True


def _string_list(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(value)


def _positive_int(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def load_campaign(path: Path | str) -> CampaignDefinition:
    """Load and validate a campaign YAML document."""

    source_path = Path(path).resolve()
    raw = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Campaign YAML root must be a mapping")
    schema_version = str(raw.get("schema_version", ""))
    if schema_version not in {"1.0", "1.1"}:
        raise ValueError("Campaign schema_version must be 1.0 or 1.1")
    campaign = raw.get("campaign")
    if not isinstance(campaign, dict):
        raise ValueError("campaign must be a mapping")

    campaign_id = str(campaign.get("id", "")).strip()
    name = str(campaign.get("name", "")).strip()
    source_profile = str(campaign.get("source_profile", "")).strip()
    if not campaign_id or not name:
        raise ValueError("campaign.id and campaign.name are required")
    if not source_profile:
        raise ValueError("campaign.source_profile is required")

    candidate_mode = str(campaign.get("candidate_mode", "automatic"))
    if candidate_mode not in {"reviewed", "automatic"}:
        raise ValueError("candidate_mode must be reviewed or automatic")
    target_profile = str(campaign.get("default_target_profile", "calculated_outputs"))
    if target_profile not in {"calculated_outputs", "all_active_variables"}:
        raise ValueError(
            "default_target_profile must be calculated_outputs or all_active_variables"
        )

    stage_rows = campaign.get("stages")
    if not isinstance(stage_rows, list) or not stage_rows:
        raise ValueError("campaign.stages must be a non-empty list")
    stages = []
    seen_ids: set[str] = set()
    for index, row in enumerate(stage_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"stages[{index}] must be a mapping")
        stage_id = str(row.get("id", "")).strip()
        stage_name = str(row.get("name", stage_id)).strip()
        if not stage_id or stage_id in seen_ids:
            raise ValueError(f"Invalid or duplicate stage id: {stage_id}")
        seen_ids.add(stage_id)
        block_value = row.get("block_id")
        block_id = str(block_value).strip() if block_value is not None else None
        has_range = "equation_start" in row or "equation_end" in row
        if bool(block_id) == has_range:
            raise ValueError(
                f"Stage {stage_id} must define exactly one of block_id or equation range"
            )
        start: Optional[int] = None
        end: Optional[int] = None
        if has_range:
            start = _positive_int(
                row.get("equation_start"),
                f"stages[{index}].equation_start",
            )
            end = _positive_int(
                row.get("equation_end"),
                f"stages[{index}].equation_end",
            )
            if end < start:
                raise ValueError(f"Invalid equation range for stage {stage_id}")
        target_mode = str(row.get("target_mode", "default"))
        if target_mode not in {"default", "replace", "extend"}:
            raise ValueError(f"Invalid target_mode for stage {stage_id}")
        stages.append(
            CampaignStage(
                stage_id=stage_id,
                name=stage_name,
                equation_start=start,
                equation_end=end,
                block_id=block_id,
                targets=_string_list(row.get("targets"), f"stages[{index}].targets"),
                target_mode=target_mode,
                approved_candidates=_string_list(
                    row.get("approved_candidates"),
                    f"stages[{index}].approved_candidates",
                ),
                prohibited_candidates=_string_list(
                    row.get("prohibited_candidates"),
                    f"stages[{index}].prohibited_candidates",
                ),
            )
        )

    costs_raw: Optional[Dict[Any, Any]] = campaign.get("sensor_costs")
    costs: Dict[str, int] = {}
    if costs_raw is not None:
        if not isinstance(costs_raw, dict):
            raise ValueError("sensor_costs must be a mapping")
        for variable, value in costs_raw.items():
            if not isinstance(variable, str):
                raise ValueError("sensor_costs keys must be strings")
            costs[variable] = _positive_int(value, f"sensor_costs.{variable}")

    solver_raw = campaign.get("solver", {})
    if not isinstance(solver_raw, dict):
        raise ValueError("solver must be a mapping")
    time_limit_s = float(solver_raw.get("time_limit_s", 60.0))
    retry_raw = solver_raw.get(
        "retry_time_limits_s",
        [time_limit_s, 300.0, 600.0],
    )
    if not isinstance(retry_raw, list) or not retry_raw:
        raise ValueError("solver.retry_time_limits_s must be a non-empty list")
    retry_limits = tuple(float(value) for value in retry_raw)
    max_tears_raw = solver_raw.get("max_tears")
    max_tears = (
        None
        if max_tears_raw is None
        else _positive_int(max_tears_raw, "solver.max_tears")
    )
    solver = CampaignSolverConfig(
        time_limit_s=time_limit_s,
        random_seed=int(solver_raw.get("random_seed", 42)),
        use_structural_preprocessing=bool(
            solver_raw.get("use_structural_preprocessing", True)
        ),
        retry_time_limits_s=retry_limits,
        decompose_components=bool(
            solver_raw.get("decompose_components", True)
        ),
        max_tears=max_tears,
        num_search_workers=_positive_int(
            solver_raw.get("num_search_workers", 1),
            "solver.num_search_workers",
        ),
    )
    if solver.time_limit_s <= 0 or any(value <= 0 for value in retry_limits):
        raise ValueError("Solver time limits must be positive")

    return CampaignDefinition(
        schema_version=schema_version,
        campaign_id=campaign_id,
        name=name,
        source_profile=source_profile,
        candidate_mode=candidate_mode,
        default_target_profile=target_profile,
        stages=tuple(stages),
        sensor_costs=costs,
        solver=solver,
        source_path=str(source_path),
        normalize_declared_duplicates=bool(
            campaign.get("normalize_declared_duplicates", True)
        ),
    )

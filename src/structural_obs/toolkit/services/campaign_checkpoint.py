#!/usr/bin/env python3
"""Canonical fingerprints and checkpoint metadata for additive campaigns."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class StageCheckpoint:
    """Reusable stage metadata stored outside the XLSX workbook."""

    stage_id: str
    stage_index: int
    input_sha256: str
    reusable: bool
    global_certificate: str


@dataclass(frozen=True)
class CampaignCheckpoint:
    """Versioned checkpoint manifest."""

    schema_version: str
    campaign_id: str
    semantics_version: str
    stages: tuple[StageCheckpoint, ...]


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    """Hash a JSON-compatible payload using stable ordering and separators."""

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def load_checkpoint(path: Path) -> CampaignCheckpoint:
    """Load and validate one checkpoint manifest."""

    raw = json.loads(path.read_text(encoding="ascii"))
    if not isinstance(raw, dict):
        raise ValueError("Checkpoint root must be a mapping")
    stage_rows = raw.get("stages")
    if not isinstance(stage_rows, list):
        raise ValueError("Checkpoint stages must be a list")
    stages = tuple(StageCheckpoint(**row) for row in stage_rows)
    return CampaignCheckpoint(
        schema_version=str(raw.get("schema_version", "")),
        campaign_id=str(raw.get("campaign_id", "")),
        semantics_version=str(raw.get("semantics_version", "")),
        stages=stages,
    )


def write_checkpoint(checkpoint: CampaignCheckpoint, path: Path) -> None:
    """Write a deterministic ASCII checkpoint manifest."""

    path.write_text(
        json.dumps(asdict(checkpoint), indent=2, ensure_ascii=True),
        encoding="ascii",
    )

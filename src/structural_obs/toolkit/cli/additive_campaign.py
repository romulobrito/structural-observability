#!/usr/bin/env python3
"""CLI for additive classification and minimum instrumentation campaigns."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from structural_obs import PROJECT_ROOT
from structural_obs.toolkit.schemas.campaign_schema import load_campaign
from structural_obs.toolkit.services.additive_campaign import run_additive_campaign
from structural_obs.toolkit.services.campaign_xlsx import (
    default_campaign_run_dir,
    load_campaign_report,
    write_campaign_artifacts,
)
from structural_obs.toolkit.services.campaign_checkpoint import load_checkpoint


def main(argv: Optional[list[str]] = None) -> int:
    """Run an additive campaign and export all artifacts."""

    parser = argparse.ArgumentParser(
        description="Run an additive structural instrumentation campaign."
    )
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument(
        "--mode",
        choices=("classify", "generate-candidates", "optimize"),
        default="optimize",
    )
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--resume-from", type=Path, default=None)
    parser.add_argument("--force-from-stage", type=str, default=None)
    arguments = parser.parse_args(argv)

    campaign_path = arguments.campaign.resolve()
    campaign = load_campaign(campaign_path)
    output_dir = arguments.out_dir
    if output_dir is None:
        output_dir = default_campaign_run_dir(
            PROJECT_ROOT / "results" / "campaigns",
            campaign.campaign_id,
        )
    output_dir = output_dir.resolve()
    resume_result = None
    resume_label = None
    if arguments.resume_from is not None:
        resume_dir = arguments.resume_from.resolve()
        checkpoint = load_checkpoint(resume_dir / "campaign_checkpoint.json")
        if checkpoint.campaign_id != campaign.campaign_id:
            raise ValueError("Resume checkpoint belongs to another campaign")
        resume_result = load_campaign_report(
            resume_dir / "campaign_report.json"
        )
        resume_label = str(resume_dir)

    def persist_progress(partial_result) -> None:
        write_campaign_artifacts(
            partial_result,
            output_dir,
            campaign_yaml_path=campaign_path,
        )
        if partial_result.stages:
            stage = partial_result.stages[-1]
            print(
                f"checkpoint: stage={stage.stage_id}, "
                f"certificate={stage.global_certificate}",
                flush=True,
            )
        elif partial_result.errors:
            print(f"checkpoint: error={partial_result.errors[-1]}", flush=True)

    result = run_additive_campaign(
        campaign,
        mode=arguments.mode,
        resume_result=resume_result,
        resume_label=resume_label,
        force_from_stage=arguments.force_from_stage,
        progress_callback=persist_progress,
    )
    written = write_campaign_artifacts(
        result,
        output_dir,
        campaign_yaml_path=campaign_path,
    )

    print(f"Campaign: {campaign.campaign_id}")
    print(f"Stages: {len(result.stages)}")
    for stage in result.stages:
        placement = stage.placement
        placement_text = "not_run"
        if placement is not None:
            primary_status = placement.status_by_phase.get(
                "phase_1_min_sensor_cost",
                "UNKNOWN",
            )
            if not placement.target_covered:
                placement_text = f"no_solution, status={primary_status}"
            else:
                certificate = (
                    "certified" if placement.minimum_certified else "uncertified"
                )
                placement_text = (
                    f"cost={placement.selected_cost}, "
                    f"sensors={list(placement.selected_sensors)}, {certificate}"
                )
        print(
            f"  {stage.stage_id}: "
            f"C_cl={stage.classification.n_closed_coverage}/"
            f"{stage.classification.total_variables}, "
            f"targets={len(stage.targets)}, placement={placement_text}"
            f", certificate={stage.global_certificate}"
        )
    for error in result.errors:
        print(f"error: {error}")
    for label, path in written.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

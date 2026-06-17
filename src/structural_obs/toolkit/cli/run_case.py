#!/usr/bin/env python3
"""Unified CLI: load YAML case and run classify or min_repair."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from structural_obs import PROJECT_ROOT
from structural_obs.toolkit.schemas.loaders import load_case
from structural_obs.toolkit.services.audit_export import default_run_dir, write_run_artifacts
from structural_obs.toolkit.services.classify_service import run_case

OUT_ROOT = PROJECT_ROOT / "results" / "cases"


def _print_classification(run) -> None:
    summary = run.classification
    if summary is None:
        return
    print(
        f"Case: {summary.case_id} | objective=classify | criterion={summary.criterion}\n"
        f"  measured={summary.measured_count} | C_cl={summary.c_closed}/{summary.total_variables} "
        f"| C_ext={summary.c_external}/{summary.total_variables} "
        f"| C_dir={summary.c_direct}/{summary.total_variables}\n"
        f"  indet={summary.effective_indeterminate} | open_tears={summary.open_tears} "
        f"| criterion_ok={summary.criterion_satisfied} | status={summary.solver_status}"
    )


def _print_repair(run) -> None:
    repair = run.repair_result
    if repair is None:
        return
    print(f"Case: {run.case.case_id} | objective=min_repair | criterion=C_cl")
    print(f"  base_measured={len(repair.base_measured)} | candidates={list(repair.candidate_pool)}")
    if repair.minimum_additions is None:
        print("  No full closed coverage found within search limit.")
        return
    print(f"  minimum_additions k={repair.minimum_additions} | optima={len(repair.optimal_solutions)}")
    for row in repair.optimal_solutions:
        added = ", ".join(row.added)
        print(
            f"    +[{added}] -> C_cl={row.metrics.closed_fraction} "
            f"status={row.metrics.solver_status}"
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a YAML case (classify or min_repair) and export audit artifacts."
    )
    parser.add_argument(
        "--case",
        required=True,
        type=Path,
        help="Path to case YAML (e.g. cases/urs_pdf_real.yaml).",
    )
    parser.add_argument(
        "--objective",
        choices=("classify", "min_repair"),
        default=None,
        help="Override analysis.objective from the YAML file.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: results/cases/<case_id>/...).",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Print summary only; do not write artifacts.",
    )
    args = parser.parse_args(argv)

    case_path = args.case
    if not case_path.is_file():
        print(f"Case file not found: {case_path}", file=sys.stderr)
        return 1

    case_def = load_case(case_path)
    if args.objective is not None:
        from dataclasses import replace

        from structural_obs.toolkit.schemas.case_schema import AnalysisConfig

        analysis = AnalysisConfig(
            objective=args.objective,
            criterion=case_def.analysis.criterion,
            repair=case_def.analysis.repair,
        )
        case_def = replace(case_def, analysis=analysis)

    try:
        run = run_case(case_def)
    except ValueError as exc:
        print(f"Run failed: {exc}", file=sys.stderr)
        return 2

    if run.objective == "classify":
        _print_classification(run)
    else:
        _print_repair(run)

    if not args.no_export:
        out_dir = args.out_dir or default_run_dir(
            case_def.case_id, run.objective, OUT_ROOT
        )
        artifacts = write_run_artifacts(run, out_dir)
        print(f"\nArtifacts written to {out_dir}")
        for key, path in artifacts.items():
            print(f"  {key}: {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

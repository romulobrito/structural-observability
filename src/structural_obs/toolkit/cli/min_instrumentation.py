#!/usr/bin/env python3
"""CLI: minimum instrumentation under PDF premises (CP-SAT tearing, C_cl criterion)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from typing import Dict, List, Set

import pandas as pd

from structural_obs import PROJECT_ROOT
from structural_obs.tearing.core import TearingConfig
from structural_obs.toolkit.premises import (
    FAILED_METERS_PDF,
    IDEAL_MEASURED_PDF,
    REAL_MEASURED_PDF,
    pairs_tested_in_pdf,
    repair_candidates,
)
from structural_obs.toolkit.services.min_repair import (
    evaluate_baseline,
    find_minimum_repair,
    find_redundant_sensors,
    greedy_minimum_subset,
    row_to_dict,
)

OUT_ROOT = PROJECT_ROOT / "results" / "min_instrumentation"


def _print_row(prefix: str, row) -> None:
    m = row.metrics
    added = ", ".join(row.added) if row.added else "(none)"
    print(
        f"{prefix} measured={row.total_measured} added=[{added}] "
        f"C_cl={m.closed_fraction} C_ext={m.c_external}/{m.total_variables} "
        f"C_dir={m.c_direct}/{m.total_variables} indet={m.effective_indeterminate} "
        f"open_tears={m.open_tears} status={m.solver_status}"
    )


def run_ideal_analysis(config) -> Dict[str, object]:
    """PDF Sec. 4.1: baseline and redundancy / greedy minimum subset."""
    scenario_key = "ideal"
    base: Set[str] = set(IDEAL_MEASURED_PDF)
    baseline = evaluate_baseline(scenario_key, base, config)
    print("\n=== PDF Sec. 4.1 -- Ideal (26 measures) ===")
    _print_row("Baseline", baseline)

    _, redundant = find_redundant_sensors(scenario_key, base, config)
    print(f"Single-sensor removals that preserve C_cl=|V|: {len(redundant)}")
    if redundant:
        print(f"  Redundant (drop-one safe): {redundant}")

    min_subset, trail = greedy_minimum_subset(scenario_key, base, config)
    print(f"Greedy minimum subset from ideal: {len(min_subset)} sensors")
    print(f"  Set: {sorted(min_subset)}")
    if len(min_subset) < len(base):
        print(f"  Removed vs PDF ideal: {sorted(base - min_subset)}")

    return {
        "section": "4.1",
        "baseline": row_to_dict(baseline),
        "redundant_drop_one": redundant,
        "greedy_minimum_subset": sorted(min_subset),
        "greedy_removal_steps": len(trail),
    }


def run_real_baseline(config) -> Dict[str, object]:
    """PDF Sec. 4.2: real operational base."""
    scenario_key = "real"
    base: Set[str] = set(REAL_MEASURED_PDF)
    baseline = evaluate_baseline(scenario_key, base, config)
    print("\n=== PDF Sec. 4.2 -- Real (22 measures) ===")
    _print_row("Baseline", baseline)
    return {"section": "4.2", "baseline": row_to_dict(baseline)}


def run_repair_search(config, pool_name: str) -> Dict[str, object]:
    """PDF Sec. 4.2.3: minimum repair from real base."""
    scenario_key = "real"
    base: Set[str] = set(REAL_MEASURED_PDF)
    candidates = repair_candidates(pool_name)
    print(f"\n=== PDF Sec. 4.2.3 -- Minimum repair (pool={pool_name}) ===")
    print(f"Base: {len(base)} measures | Candidates: {candidates}")

    result = find_minimum_repair(scenario_key, base, candidates, config)
    if result.minimum_additions is None:
        print("No full closed coverage found within candidate pool.")
    else:
        print(f"Minimum additions k={result.minimum_additions} | Optimal solutions: {len(result.optimal_solutions)}")
        for row in result.optimal_solutions:
            _print_row("  Optimal", row)

    pdf_pairs = pairs_tested_in_pdf()
    pdf_pair_hits = []
    for a, b in pdf_pairs:
        target = tuple(sorted((a, b)))
        for row in result.optimal_solutions:
            if row.added == target:
                pdf_pair_hits.append(target)
                break
    print(f"PDF-tested pairs among optima: {pdf_pair_hits}")

    return {
        "section": "4.2.3",
        "candidate_pool": pool_name,
        "failed_meters_pdf": sorted(FAILED_METERS_PDF),
        "minimum_additions": result.minimum_additions,
        "optimal_solutions": [row_to_dict(r) for r in result.optimal_solutions],
        "pdf_pairs_among_optima": [list(p) for p in pdf_pair_hits],
        "evaluated_count": len(result.all_evaluated),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Minimum instrumentation search aligned with PDF URS premises. "
            "Uses CP-SAT tearing and full closed coverage C_cl == |V|."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("all", "ideal", "real", "repair"),
        default="all",
        help="Analysis block to run (default: all PDF sections).",
    )
    parser.add_argument(
        "--candidate-pool",
        choices=("failed", "extended"),
        default="failed",
        help="Repair candidates for Sec. 4.2.3 (default: failed meters from PDF).",
    )
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--allow-feasible", action="store_true")
    args = parser.parse_args()

    config = TearingConfig(time_limit_s=args.time_limit, require_optimal=not args.allow_feasible)

    print("URS PDF minimum instrumentation (CP-SAT tearing)")
    print(f"Criterion: C_cl == |V| (fully closed structural coverage)")
    print(f"Failed meters (PDF): {sorted(FAILED_METERS_PDF)}")

    report: Dict[str, object] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "criterion": "C_cl == |V|",
        "config": {"time_limit_s": args.time_limit, "require_optimal": not args.allow_feasible},
    }

    if args.mode in ("all", "ideal"):
        report["ideal"] = run_ideal_analysis(config)
    if args.mode in ("all", "real"):
        report["real"] = run_real_baseline(config)
    if args.mode in ("all", "repair"):
        report["repair"] = run_repair_search(config, args.candidate_pool)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUT_ROOT / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    json_path = run_dir / "min_instrumentation_report.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    rows: List[Dict[str, object]] = []
    for block in ("ideal", "real", "repair"):
        if block not in report:
            continue
        data = report[block]
        if "baseline" in data:
            rows.append(data["baseline"])
        for item in data.get("optimal_solutions", []):
            rows.append(item)
    if rows:
        flat_rows = []
        for r in rows:
            m = r["metrics"]
            flat_rows.append({
                "scenario_key": r["scenario_key"],
                "search_kind": r["search_kind"],
                "base_count": r["base_count"],
                "added": ", ".join(r["added"]),
                "total_measured": r["total_measured"],
                "C_cl": m["c_closed"],
                "V": m["total_variables"],
                "C_ext": m["c_external"],
                "C_dir": m["c_direct"],
                "effective_indeterminate": m["effective_indeterminate"],
                "open_tears": m["open_tears"],
                "fully_closed": m["fully_closed"],
                "solver_status": m["solver_status"],
            })
        pd.DataFrame(flat_rows).to_csv(run_dir / "min_instrumentation_summary.csv", index=False)

    print(f"\nReport: {json_path}")
    print(f"CSV:    {run_dir / 'min_instrumentation_summary.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

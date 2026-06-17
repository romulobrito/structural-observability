#!/usr/bin/env python3
"""Export audit artifacts for a case run (YAML snapshot, JSON, CSV)."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from structural_obs.toolkit.schemas.loaders import save_case
from structural_obs.toolkit.schemas.case_schema import CaseDefinition
from structural_obs.toolkit.services.classify_service import (
    CaseRunResult,
    repair_rows_to_csv_rows,
    repair_result_to_dict,
    summary_to_dict,
    tearing_result_to_dict,
)


def default_run_dir(case_id: str, objective: str, base: Path) -> Path:
    """Build a timestamped output directory under base."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return base / case_id / f"{objective}_{stamp}"


def build_report_payload(run: CaseRunResult) -> Dict[str, Any]:
    """Assemble a JSON-serializable audit report."""
    case = run.case
    payload: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "case_id": case.case_id,
        "case_name": case.name,
        "section": case.section,
        "objective": run.objective,
        "criterion": case.analysis.criterion,
        "source_path": case.source_path,
        "equations_profile": case.equations_profile,
        "solver": asdict(case.solver),
    }
    if run.classification is not None:
        payload["classification"] = summary_to_dict(run.classification)
    if run.tearing_result is not None:
        payload["tearing"] = tearing_result_to_dict(run.tearing_result)
    if run.repair_result is not None:
        payload["repair"] = repair_result_to_dict(run.repair_result)
    return payload


def write_run_artifacts(
    run: CaseRunResult,
    out_dir: Path,
    *,
    write_case_yaml: bool = True,
) -> Dict[str, Path]:
    """Write YAML case snapshot, JSON report, and CSV summary."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}

    if write_case_yaml:
        case_path = out_dir / "case_snapshot.yaml"
        save_case(run.case, case_path)
        written["case_yaml"] = case_path

    report_path = out_dir / "run_report.json"
    report_path.write_text(
        json.dumps(build_report_payload(run), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    written["json"] = report_path

    csv_path = out_dir / "run_summary.csv"
    rows: List[Dict[str, Any]] = []
    if run.classification is not None and run.tearing_result is not None:
        tr = run.tearing_result
        rows.append(
            {
                "case_id": run.case.case_id,
                "objective": "classify",
                "measured_count": len(run.case.instrumentation.measured),
                "C_cl": tr.n_closed_coverage,
                "V": tr.total_variables,
                "C_ext": tr.n_external_reach,
                "C_dir": tr.n_direct,
                "effective_indeterminate": len(tr.effective_indeterminate),
                "open_tears": len(tr.tears_open),
                "criterion_satisfied": run.classification.criterion_satisfied,
                "solver_status": run.classification.solver_status,
            }
        )
    if run.repair_rows:
        rows.extend(repair_rows_to_csv_rows(list(run.repair_rows)))
    if rows:
        pd.DataFrame(rows).to_csv(csv_path, index=False)
        written["csv"] = csv_path

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "case_id": run.case.case_id,
                "objective": run.objective,
                "artifacts": {key: str(path.name) for key, path in written.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    written["manifest"] = manifest_path
    return written


def export_resolved_case_yaml(case: CaseDefinition, path: Path) -> Path:
    """Write resolved case (with inline equations if profile was used)."""
    resolved = CaseDefinition(
        schema_version=case.schema_version,
        case_id=case.case_id,
        name=case.name,
        section=case.section,
        equations=case.equations,
        instrumentation=case.instrumentation,
        allowed_outputs=case.allowed_outputs,
        analysis=case.analysis,
        solver=case.solver,
        equations_profile=None,
        source_path=case.source_path,
    )
    save_case(resolved, path)
    return path

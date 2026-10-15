#!/usr/bin/env python3
"""Export additive campaign results to JSON, YAML, CSV, and XLSX."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

import pandas as pd

from structural_obs.toolkit.services.additive_campaign import (
    AdditiveCampaignResult,
    CampaignStageResult,
    ComponentCertificate,
)
from structural_obs.tearing.core import TearingResult
from structural_obs.toolkit.services.campaign_checkpoint import (
    CampaignCheckpoint,
    StageCheckpoint,
    write_checkpoint,
)
from structural_obs.toolkit.services.candidate_generation import (
    CandidateSuggestion,
    suggestion_entered_tier,
    suggestions_to_yaml,
)
from structural_obs.toolkit.services.integrated_sensor_placement import (
    IntegratedPlacementResult,
)
from structural_obs.toolkit.services.solver_retry import SolverAttemptRecord


def default_campaign_run_dir(base: Path, campaign_id: str) -> Path:
    """Build a timestamped campaign output directory."""

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return base / campaign_id / f"run_{stamp}"


def _json_default(value: object) -> object:
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object is not JSON serializable: {type(value).__name__}")


def _tearing_from_dict(raw: Mapping[str, Any]) -> TearingResult:
    payload = dict(raw)
    payload["tear_pairs"] = [
        tuple(pair) for pair in payload.get("tear_pairs", [])
    ]
    payload["cut_graph_edges"] = [
        tuple(pair) for pair in payload.get("cut_graph_edges", [])
    ]
    payload["full_graph_edges"] = [
        tuple(pair) for pair in payload.get("full_graph_edges", [])
    ]
    return TearingResult(**payload)


def _placement_from_dict(
    raw: Mapping[str, Any] | None,
) -> IntegratedPlacementResult | None:
    if raw is None:
        return None
    payload = dict(raw)
    for field_name in (
        "selected_sensors",
        "target_variables",
        "retained_equations",
        "removed_equations",
    ):
        payload[field_name] = tuple(payload.get(field_name, []))
    return IntegratedPlacementResult(**payload)


def load_campaign_report(path: Path) -> AdditiveCampaignResult:
    """Load a campaign report for signature-based resume."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Campaign report root must be a mapping")
    stages = []
    for row in raw.get("stages", []):
        suggestions = tuple(
            CandidateSuggestion(
                variable=str(item["variable"]),
                reasons=tuple(item.get("reasons", [])),
                distance_to_uncovered_target=int(
                    item["distance_to_uncovered_target"]
                ),
                approved=bool(item.get("approved", False)),
            )
            for item in row.get("candidate_suggestions", [])
        )
        certificates = tuple(
            ComponentCertificate(
                component_id=str(item["component_id"]),
                equations=tuple(item.get("equations", [])),
                variables=tuple(item.get("variables", [])),
                targets=tuple(item.get("targets", [])),
                selected_sensors=tuple(item.get("selected_sensors", [])),
                selected_cost=int(item.get("selected_cost", 0)),
                classification_certified=bool(
                    item.get("classification_certified", False)
                ),
                placement_certified=bool(
                    item.get("placement_certified", False)
                ),
                validation_ok=bool(item.get("validation_ok", False)),
                status=str(item.get("status", "UNKNOWN")),
            )
            for item in row.get("component_certificates", [])
        )
        attempts = tuple(
            SolverAttemptRecord(**item)
            for item in row.get("solver_attempts", [])
        )
        stages.append(
            CampaignStageResult(
                stage_id=str(row["stage_id"]),
                stage_name=str(row["stage_name"]),
                stage_index=int(row["stage_index"]),
                added_equations=tuple(row.get("added_equations", [])),
                cumulative_equations=tuple(
                    row.get("cumulative_equations", [])
                ),
                targets=tuple(row.get("targets", [])),
                base_measured=tuple(row.get("base_measured", [])),
                known_constants=tuple(row.get("known_constants", [])),
                classification=_tearing_from_dict(row["classification"]),
                candidate_suggestions=suggestions,
                approved_candidates=tuple(
                    row.get("approved_candidates", [])
                ),
                placement=_placement_from_dict(row.get("placement")),
                validation=(
                    _tearing_from_dict(row["validation"])
                    if row.get("validation") is not None
                    else None
                ),
                warnings=tuple(row.get("warnings", [])),
                component_count=int(row.get("component_count", 1)),
                component_certificates=certificates,
                solver_attempts=attempts,
                input_sha256=str(row.get("input_sha256", "")),
                reused_from_run=row.get("reused_from_run"),
                global_certificate=str(
                    row.get("global_certificate", "partial")
                ),
                candidate_tier=int(row.get("candidate_tier", 0)),
                normalized_removed_equations=tuple(
                    row.get("normalized_removed_equations", [])
                ),
            )
        )
    return AdditiveCampaignResult(
        campaign_id=str(raw["campaign_id"]),
        campaign_name=str(raw["campaign_name"]),
        source_path=str(raw["source_path"]),
        stages=tuple(stages),
        duplicate_equation_groups=tuple(
            tuple(group)
            for group in raw.get("duplicate_equation_groups", [])
        ),
        errors=tuple(raw.get("errors", [])),
        semantics_version=str(
            raw.get("semantics_version", "additive_campaign_v1")
        ),
        candidate_mode=str(raw.get("candidate_mode", "automatic")),
    )


def _global_status(statuses: Mapping[str, str]) -> str:
    unique = set(statuses.values())
    return "OPTIMAL" if unique == {"OPTIMAL"} else ",".join(sorted(unique))


def _summary_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        baseline = stage.classification
        placement = stage.placement
        validation = stage.validation
        target_count = len(stage.targets)
        baseline_target_closed = len(
            set(stage.targets) & baseline.closed_coverage_variables
        )
        rows.append(
            {
                "stage_index": stage.stage_index,
                "stage_id": stage.stage_id,
                "stage_name": stage.stage_name,
                "equations": baseline.total_equations,
                "variables": baseline.total_variables,
                "components": stage.component_count,
                "global_certificate": stage.global_certificate,
                "candidate_tier": stage.candidate_tier,
                "input_sha256": stage.input_sha256,
                "reused_from_run": stage.reused_from_run,
                "base_measured": len(stage.base_measured),
                "known_constants": len(stage.known_constants),
                "targets": target_count,
                "baseline_targets_closed": baseline_target_closed,
                "baseline_C_dir": baseline.n_direct,
                "baseline_C_cl": baseline.n_closed_coverage,
                "baseline_C_ext": baseline.n_external_reach,
                "baseline_open_tears": len(baseline.tears_open),
                "baseline_status": _global_status(baseline.status_by_phase),
                "approved_candidates": len(stage.approved_candidates),
                "selected_sensors": (
                    len(placement.selected_sensors) if placement else None
                ),
                "selected_cost": placement.selected_cost if placement else None,
                "minimum_certified": (
                    placement.minimum_certified if placement else None
                ),
                "placement_primary_status": (
                    placement.status_by_phase.get(
                        "phase_1_min_sensor_cost",
                        "UNKNOWN",
                    )
                    if placement
                    else None
                ),
                "placement_target_covered": (
                    placement.target_covered if placement else None
                ),
                "validation_C_cl": (
                    validation.n_closed_coverage if validation else None
                ),
                "validation_status": (
                    _global_status(validation.status_by_phase)
                    if validation
                    else None
                ),
                "warnings": " | ".join(stage.warnings),
            }
        )
    return rows


def _class_map(stage: CampaignStageResult) -> Dict[str, str]:
    result = stage.classification
    classes = {
        "measured": result.measured,
        "known_constant": result.known_constants,
        "inferred_direct": result.inferred_direct,
        "inferred_closed_loop": result.inferred_closed_loop,
        "tear_closed": result.tears_closed,
        "conditioned_open": result.inferred_conditioned_open,
        "tear_closed_external": result.tears_closed_external,
        "tear_open": result.tears_open,
        "indeterminate_pure": result.indeterminate_pure,
    }
    return {
        variable: class_name
        for class_name, variables in classes.items()
        for variable in variables
    }


def _variable_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        classification = stage.classification
        class_by_variable = _class_map(stage)
        target_set = set(stage.targets)
        for variable in sorted(class_by_variable):
            rows.append(
                {
                    "stage_index": stage.stage_index,
                    "stage_id": stage.stage_id,
                    "variable": variable,
                    "class": class_by_variable[variable],
                    "is_target": variable in target_set,
                    "output_equation": classification.output_equation.get(variable),
                    "level": classification.levels.get(variable),
                    "uses_tears": ", ".join(
                        classification.output_uses_tears.get(variable, [])
                    ),
                    "externally_conditioned": (
                        variable in classification.externally_conditioned
                    ),
                }
            )
    return rows


def _target_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        baseline_closed = stage.classification.closed_coverage_variables
        validation_closed = (
            stage.validation.closed_coverage_variables
            if stage.validation
            else set()
        )
        for target in stage.targets:
            rows.append(
                {
                    "stage_index": stage.stage_index,
                    "stage_id": stage.stage_id,
                    "target": target,
                    "baseline_closed": target in baseline_closed,
                    "validation_closed": (
                        target in validation_closed if stage.validation else None
                    ),
                }
            )
    return rows


def _equation_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        classification = stage.classification
        output_by_equation = {
            equation: variable
            for variable, equation in classification.output_equation.items()
            if equation
        }
        tear_by_equation: Dict[str, List[str]] = {}
        for equation, variable in classification.tear_pairs:
            tear_by_equation.setdefault(equation, []).append(variable)
        for equation in stage.cumulative_equations:
            rows.append(
                {
                    "stage_index": stage.stage_index,
                    "stage_id": stage.stage_id,
                    "equation": equation,
                    "selected_output": output_by_equation.get(equation),
                    "local_tears": ", ".join(
                        sorted(tear_by_equation.get(equation, []))
                    ),
                    "retained_by_preprocessing": (
                        equation in classification.retained_equations
                    ),
                }
            )
    return rows


def _phase_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        runs = [("baseline", stage.classification)]
        if stage.validation:
            runs.append(("validation", stage.validation))
        for run_kind, run in runs:
            for phase, status in run.status_by_phase.items():
                rows.append(
                    {
                        "stage_index": stage.stage_index,
                        "stage_id": stage.stage_id,
                        "run_kind": run_kind,
                        "phase": phase,
                        "status": status,
                        "objective": run.objective_by_phase.get(phase),
                        "time_s": run.time_by_phase_s.get(phase),
                    }
                )
        if stage.placement:
            for phase, status in stage.placement.status_by_phase.items():
                rows.append(
                    {
                        "stage_index": stage.stage_index,
                        "stage_id": stage.stage_id,
                        "run_kind": "placement",
                        "phase": phase,
                        "status": status,
                        "objective": stage.placement.objective_by_phase.get(phase),
                        "time_s": stage.placement.time_by_phase_s.get(phase),
                    }
                )
    return rows


def _candidate_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        considered = set(stage.approved_candidates)
        selected = set(
            stage.placement.selected_sensors if stage.placement else ()
        )
        for suggestion in stage.candidate_suggestions:
            entered_tier = suggestion_entered_tier(suggestion)
            if suggestion.variable in selected:
                disposition = "selected"
            elif suggestion.variable in considered:
                disposition = "considered_not_selected"
            elif (
                result.candidate_mode == "automatic"
                and stage.candidate_tier
                and entered_tier > stage.candidate_tier
            ):
                disposition = "rejected_later_tier"
            else:
                disposition = "rejected_not_considered"
            rows.append(
                {
                    "stage_index": stage.stage_index,
                    "stage_id": stage.stage_id,
                    "variable": suggestion.variable,
                    "reasons": ", ".join(suggestion.reasons),
                    "distance_to_target": suggestion.distance_to_uncovered_target,
                    "entered_tier": entered_tier,
                    "used_tier": stage.candidate_tier,
                    "considered": suggestion.variable in considered,
                    "disposition": disposition,
                    "approved": suggestion.variable in considered,
                }
            )
    return rows


def _instrumentation_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        if not stage.placement:
            continue
        for variable in stage.placement.selected_sensors:
            rows.append(
                {
                    "stage_index": stage.stage_index,
                    "stage_id": stage.stage_id,
                    "variable": variable,
                    "selected_cost": stage.placement.selected_cost,
                    "minimum_certified": stage.placement.minimum_certified,
                    "target_covered": stage.placement.target_covered,
                }
            )
    return rows


def _approved_candidate_rows(
    result: AdditiveCampaignResult,
) -> List[Dict[str, Any]]:
    return [
        {
            "stage_index": stage.stage_index,
            "stage_id": stage.stage_id,
            "variable": variable,
            "selected": bool(
                stage.placement
                and variable in stage.placement.selected_sensors
            ),
        }
        for stage in result.stages
        for variable in stage.approved_candidates
    ]


def _validation_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        if stage.validation is None:
            continue
        validation = stage.validation
        rows.append(
            {
                "stage_index": stage.stage_index,
                "stage_id": stage.stage_id,
                "C_dir": validation.n_direct,
                "C_cl": validation.n_closed_coverage,
                "C_ext": validation.n_external_reach,
                "variables": validation.total_variables,
                "targets_closed": (
                    set(stage.targets) <= validation.closed_coverage_variables
                ),
                "execution_graph_dag": validation.execution_graph_is_dag,
                "status": _global_status(validation.status_by_phase),
            }
        )
    return rows


def _component_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = []
    for stage in result.stages:
        for index, component in enumerate(
            stage.classification.cyclic_sccs_full_graph,
            start=1,
        ):
            rows.append(
                {
                    "stage_index": stage.stage_index,
                    "stage_id": stage.stage_id,
                    "component_type": "cyclic_scc",
                    "scc_index": index,
                    "variables": ", ".join(component),
                }
            )
    return rows


def _incidence_component_rows(
    result: AdditiveCampaignResult,
) -> List[Dict[str, Any]]:
    return [
        {
            "stage_index": stage.stage_index,
            "stage_id": stage.stage_id,
            "component_id": certificate.component_id,
            "equations": len(certificate.equations),
            "variables": len(certificate.variables),
            "targets": len(certificate.targets),
            "selected_sensors": ", ".join(certificate.selected_sensors),
            "selected_cost": certificate.selected_cost,
            "classification_certified": (
                certificate.classification_certified
            ),
            "placement_certified": certificate.placement_certified,
            "validation_ok": certificate.validation_ok,
            "status": certificate.status,
        }
        for stage in result.stages
        for certificate in stage.component_certificates
    ]


def _retry_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    return [
        {
            "stage_index": stage.stage_index,
            "stage_id": stage.stage_id,
            "operation": attempt.operation,
            "component_id": attempt.component_id,
            "attempt": attempt.attempt,
            "time_limit_s": attempt.time_limit_s,
            "terminal_status": attempt.terminal_status,
            "certified": attempt.certified,
            "error": attempt.error,
        }
        for stage in result.stages
        for attempt in stage.solver_attempts
    ]


def _resume_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    return [
        {
            "stage_index": stage.stage_index,
            "stage_id": stage.stage_id,
            "input_sha256": stage.input_sha256,
            "global_certificate": stage.global_certificate,
            "reused_from_run": stage.reused_from_run,
        }
        for stage in result.stages
    ]


def _warning_rows(result: AdditiveCampaignResult) -> List[Dict[str, Any]]:
    rows = [
        {
            "stage_index": stage.stage_index,
            "stage_id": stage.stage_id,
            "warning": warning,
        }
        for stage in result.stages
        for warning in stage.warnings
    ]
    rows.extend(
        {
            "stage_index": None,
            "stage_id": None,
            "warning": error,
        }
        for error in result.errors
    )
    return rows


def _write_sheet(
    writer: pd.ExcelWriter,
    name: str,
    rows: Iterable[Mapping[str, Any]],
) -> None:
    frame = pd.DataFrame(list(rows))
    frame.to_excel(writer, sheet_name=name, index=False)


def write_campaign_artifacts(
    result: AdditiveCampaignResult,
    output_dir: Path,
    *,
    campaign_yaml_path: Path,
) -> Dict[str, Path]:
    """Write complete, auditable campaign artifacts."""

    output_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}

    snapshot_path = output_dir / "campaign_snapshot.yaml"
    snapshot_path.write_text(
        campaign_yaml_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    written["campaign_yaml"] = snapshot_path

    report_path = output_dir / "campaign_report.json"
    report_path.write_text(
        json.dumps(asdict(result), indent=2, default=_json_default),
        encoding="utf-8",
    )
    written["json"] = report_path

    checkpoint_path = output_dir / "campaign_checkpoint.json"
    write_checkpoint(
        CampaignCheckpoint(
            schema_version="1.0",
            campaign_id=result.campaign_id,
            semantics_version=result.semantics_version,
            stages=tuple(
                StageCheckpoint(
                    stage_id=stage.stage_id,
                    stage_index=stage.stage_index,
                    input_sha256=stage.input_sha256,
                    reusable=stage.global_certificate == "certified",
                    global_certificate=stage.global_certificate,
                )
                for stage in result.stages
            ),
        ),
        checkpoint_path,
    )
    written["checkpoint"] = checkpoint_path

    suggestion_path = output_dir / "candidatos_sugeridos.yaml"
    suggestion_path.write_text(
        suggestions_to_yaml(
            result.campaign_id,
            {
                stage.stage_id: stage.candidate_suggestions
                for stage in result.stages
            },
        ),
        encoding="ascii",
    )
    written["candidate_yaml"] = suggestion_path

    summary_path = output_dir / "campaign_summary.csv"
    pd.DataFrame(_summary_rows(result)).to_csv(summary_path, index=False)
    written["summary_csv"] = summary_path

    xlsx_path = output_dir / "campaign_results.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        _write_sheet(writer, "resumo_etapas", _summary_rows(result))
        _write_sheet(writer, "cobertura_alvos", _target_rows(result))
        _write_sheet(writer, "variaveis", _variable_rows(result))
        _write_sheet(writer, "equacoes", _equation_rows(result))
        _write_sheet(writer, "fases_solver", _phase_rows(result))
        _write_sheet(writer, "candidatos_sugeridos", _candidate_rows(result))
        _write_sheet(writer, "candidatos_usados", _approved_candidate_rows(result))
        _write_sheet(writer, "instrumentacao_minima", _instrumentation_rows(result))
        _write_sheet(writer, "validacao", _validation_rows(result))
        _write_sheet(writer, "componentes_scc_ciclicos", _component_rows(result))
        _write_sheet(
            writer,
            "componentes_incidencia",
            _incidence_component_rows(result),
        )
        _write_sheet(writer, "tentativas_solver", _retry_rows(result))
        _write_sheet(writer, "retomada", _resume_rows(result))
        _write_sheet(writer, "erros_avisos", _warning_rows(result))
    written["xlsx"] = xlsx_path
    return written

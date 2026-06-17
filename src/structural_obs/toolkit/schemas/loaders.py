#!/usr/bin/env python3
"""Load and save YAML case files (schema v1.0)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional

import yaml

from structural_obs.tearing.cases import urs_document_bank
from structural_obs.toolkit.schemas.case_schema import (
    AnalysisConfig,
    CaseDefinition,
    CaseDocument,
    Criterion,
    InstrumentationConfig,
    Objective,
    RepairConfig,
    SolverConfig,
    validate_case_document,
)

Equations = Dict[str, List[str]]

EQUATION_PROFILES: Dict[str, Callable[[], Equations]] = {
    "urs_document": urs_document_bank.equations_documento,
    "urs_kpi_bancos": urs_document_bank.equations_kpi_bancos,
}


def _as_str_list(value: Any, field_name: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return list(value)


def _parse_allowed_outputs(raw: Any) -> Optional[Mapping[str, frozenset[str]]]:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("allowed_outputs must be a mapping equation -> [variables]")
    parsed: Dict[str, frozenset[str]] = {}
    for eq_name, vars_list in raw.items():
        if not isinstance(eq_name, str):
            raise ValueError("allowed_outputs equation keys must be strings")
        parsed[eq_name] = frozenset(_as_str_list(vars_list, f"allowed_outputs.{eq_name}"))
    return parsed


def _parse_equations(raw: Any) -> Optional[Equations]:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("equations must be a mapping equation -> [variables]")
    equations: Equations = {}
    for eq_name, vars_list in raw.items():
        if not isinstance(eq_name, str):
            raise ValueError("equation keys must be strings")
        equations[eq_name] = _as_str_list(vars_list, f"equations.{eq_name}")
    return equations


def _parse_repair(raw: Any) -> Optional[RepairConfig]:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("analysis.repair must be a mapping")
    base = frozenset(_as_str_list(raw.get("base_measured"), "repair.base_measured"))
    candidates = tuple(_as_str_list(raw.get("candidates"), "repair.candidates"))
    pool = str(raw.get("candidate_pool", "failed"))
    max_additions = raw.get("max_additions")
    if max_additions is not None and not isinstance(max_additions, int):
        raise ValueError("repair.max_additions must be an integer or null")
    return RepairConfig(
        base_measured=base,
        candidates=candidates,
        candidate_pool=pool,
        max_additions=max_additions,
    )


def _parse_analysis(raw: Any) -> AnalysisConfig:
    if not isinstance(raw, dict):
        raise ValueError("analysis must be a mapping")
    objective = str(raw.get("objective", "classify"))
    if objective not in ("classify", "min_repair"):
        raise ValueError("analysis.objective must be 'classify' or 'min_repair'")
    criterion = str(raw.get("criterion", "C_cl"))
    if criterion not in ("C_cl", "C_ext"):
        raise ValueError("analysis.criterion must be 'C_cl' or 'C_ext'")
    return AnalysisConfig(
        objective=objective,  # type: ignore[arg-type]
        criterion=criterion,  # type: ignore[arg-type]
        repair=_parse_repair(raw.get("repair")),
    )


def _parse_solver(raw: Any) -> SolverConfig:
    if raw is None:
        return SolverConfig()
    if not isinstance(raw, dict):
        raise ValueError("solver must be a mapping")
    return SolverConfig(
        time_limit_s=float(raw.get("time_limit_s", 60.0)),
        require_optimal=bool(raw.get("require_optimal", True)),
        use_structural_preprocessing=bool(raw.get("use_structural_preprocessing", True)),
        random_seed=int(raw.get("random_seed", 42)),
    )


def _resolve_equations(doc: CaseDocument) -> Equations:
    if doc.equations is not None and doc.equations_profile is not None:
        raise ValueError("Use either equations or equations_profile, not both")
    if doc.equations is not None:
        return doc.equations
    if doc.equations_profile is not None:
        profile = doc.equations_profile
        if profile not in EQUATION_PROFILES:
            known = ", ".join(sorted(EQUATION_PROFILES))
            raise ValueError(f"Unknown equations_profile '{profile}'. Known: {known}")
        return EQUATION_PROFILES[profile]()
    raise ValueError("Case must define equations or equations_profile")


def _parse_case_document(data: Mapping[str, Any], source_path: Optional[Path]) -> CaseDocument:
    schema_version = str(data.get("schema_version", ""))
    case_raw = data.get("case")
    if not isinstance(case_raw, dict):
        raise ValueError("Top-level 'case' mapping is required")

    inst_raw = case_raw.get("instrumentation", {})
    if not isinstance(inst_raw, dict):
        raise ValueError("case.instrumentation must be a mapping")

    return CaseDocument(
        schema_version=schema_version,
        case_id=str(case_raw.get("id", "")),
        name=str(case_raw.get("name", "")),
        section=str(case_raw.get("section", "")),
        equations=_parse_equations(case_raw.get("equations")),
        equations_profile=(
            str(case_raw["equations_profile"]) if "equations_profile" in case_raw else None
        ),
        instrumentation=InstrumentationConfig(
            measured=frozenset(_as_str_list(inst_raw.get("measured"), "instrumentation.measured")),
            known_constants=frozenset(
                _as_str_list(inst_raw.get("known_constants"), "instrumentation.known_constants")
            ),
        ),
        allowed_outputs=_parse_allowed_outputs(case_raw.get("allowed_outputs")),
        analysis=_parse_analysis(case_raw.get("analysis", {"objective": "classify"})),
        solver=_parse_solver(case_raw.get("solver")),
        source_path=str(source_path) if source_path is not None else None,
    )


def load_case_document(path: Path | str) -> CaseDocument:
    """Load a YAML file into a CaseDocument (equations may be unresolved)."""
    file_path = Path(path)
    raw = yaml.safe_load(file_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid case file (expected mapping): {file_path}")
    return _parse_case_document(raw, file_path)


def load_case(path: Path | str) -> CaseDefinition:
    """Load and validate a case from YAML."""
    doc = load_case_document(path)
    if not doc.case_id:
        raise ValueError("case.id is required")
    if not doc.name:
        raise ValueError("case.name is required")
    equations = _resolve_equations(doc)
    return validate_case_document(doc, equations)


def case_to_yaml_dict(case: CaseDefinition) -> Dict[str, Any]:
    """Serialize a CaseDefinition to a YAML-compatible dict."""
    instrumentation: Dict[str, Any] = {
        "measured": sorted(case.instrumentation.measured),
        "known_constants": sorted(case.instrumentation.known_constants),
    }
    analysis: Dict[str, Any] = {
        "objective": case.analysis.objective,
        "criterion": case.analysis.criterion,
    }
    if case.analysis.repair is not None:
        repair = case.analysis.repair
        analysis["repair"] = {
            "base_measured": sorted(repair.base_measured),
            "candidates": list(repair.candidates),
            "candidate_pool": repair.candidate_pool,
            "max_additions": repair.max_additions,
        }
    payload: Dict[str, Any] = {
        "schema_version": case.schema_version,
        "case": {
            "id": case.case_id,
            "name": case.name,
            "section": case.section,
            "instrumentation": instrumentation,
            "analysis": analysis,
            "solver": {
                "time_limit_s": case.solver.time_limit_s,
                "require_optimal": case.solver.require_optimal,
                "use_structural_preprocessing": case.solver.use_structural_preprocessing,
                "random_seed": case.solver.random_seed,
            },
        },
    }
    if case.equations_profile:
        payload["case"]["equations_profile"] = case.equations_profile
    else:
        payload["case"]["equations"] = {
            eq: list(vars_list) for eq, vars_list in sorted(case.equations.items())
        }
    if case.allowed_outputs:
        payload["case"]["allowed_outputs"] = {
            eq: sorted(allowed) for eq, allowed in sorted(case.allowed_outputs.items())
        }
    return payload


def save_case(case: CaseDefinition, path: Path | str) -> None:
    """Write a CaseDefinition to YAML."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(case_to_yaml_dict(case), sort_keys=False, allow_unicode=False)
    file_path.write_text(text, encoding="utf-8")

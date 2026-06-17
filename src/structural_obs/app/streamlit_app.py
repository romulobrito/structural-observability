#!/usr/bin/env python3
"""Streamlit UI: simple Portuguese labels for classify and min_repair."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from typing import Optional

import yaml

from structural_obs import PROJECT_ROOT
from structural_obs.app.bundle import build_audit_zip
from structural_obs.app.display import (
    render_classification_details,
    render_classification_summary,
    render_milp_summary,
    render_repair_summary,
)
from structural_obs.app.presenters import present_classification, present_milp, present_repair
from structural_obs.app.ui_labels import (
    ABOUT_TEXT,
    ABOUT_TITLE,
    ADVANCED_MODE,
    APP_SUBTITLE,
    APP_TITLE,
    CRITERION_LINE,
    DOWNLOAD_ZIP,
    ERROR_INVALID_CASE,
    ERROR_RUN_FAILED,
    PRESET_IDEAL,
    PRESET_LABEL,
    PRESET_MILP_GLOBAL,
    PRESET_MILP_REPAIR,
    PRESET_MILP_VERIFY_IDEAL,
    PRESET_MILP_VERIFY_REAL,
    PRESET_REAL,
    PRESET_REPAIR,
    REPAIR_BASELINE_INFO,
    RUN_DIAGNOSTIC,
    RUN_MILP,
    RUN_REPAIR,
    SECTION_REPAIR_BEFORE,
    SIDEBAR_HEADER,
    SIDEBAR_TIME_LIMIT,
    SPINNER_DIAGNOSTIC,
    SPINNER_MILP,
    SPINNER_REPAIR,
    TAB_DIAGNOSTIC,
    TAB_MILP,
    TAB_REPAIR,
    UPLOAD_YAML,
    YAML_EDITOR,
    MILP_PRESET_HINTS,
    MILP_WARNING,
)
from structural_obs.toolkit.schemas.case_schema import AnalysisConfig
from structural_obs.toolkit.services.classify_service import CaseRunResult, run_case
from structural_obs.toolkit.schemas.loaders import load_case

CASES_DIR = PROJECT_ROOT / "cases"

PRESET_PATHS: dict[str, Path] = {
    PRESET_IDEAL: CASES_DIR / "urs_pdf_ideal.yaml",
    PRESET_REAL: CASES_DIR / "urs_pdf_real.yaml",
    PRESET_REPAIR: CASES_DIR / "urs_pdf_repair.yaml",
    PRESET_MILP_GLOBAL: CASES_DIR / "urs_milp_global.yaml",
    PRESET_MILP_VERIFY_REAL: CASES_DIR / "urs_milp_verify_real.yaml",
    PRESET_MILP_VERIFY_IDEAL: CASES_DIR / "urs_milp_verify_ideal.yaml",
    PRESET_MILP_REPAIR: CASES_DIR / "urs_milp_repair.yaml",
}


def _load_preset(path: Path):
    """Load a validated case from a preset path."""
    return load_case(path)


def _load_yaml_text(text: str, source: str):
    """Parse YAML text into a validated case."""
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise ValueError(ERROR_INVALID_CASE)
    tmp = PROJECT_ROOT / ".tmp_case.yaml"
    try:
        tmp.write_text(text, encoding="utf-8")
        return load_case(tmp)
    finally:
        if tmp.exists():
            tmp.unlink()


def _render_classification(run: CaseRunResult, advanced: bool) -> None:
    import streamlit as st

    view = present_classification(run)
    st.success(view.headline)
    render_classification_summary(view)
    render_classification_details(
        view,
        advanced,
        run.tearing_result,
    )


def _render_repair(run: CaseRunResult, advanced: bool) -> None:
    import streamlit as st

    view = present_repair(run)
    if view.minimum_additions is None:
        st.warning(view.headline)
    else:
        st.success(view.headline)

    render_repair_summary(view)

    st.subheader(SECTION_REPAIR_BEFORE)
    st.info(view.baseline.headline)
    render_classification_summary(view.baseline)
    render_classification_details(view.baseline, advanced, view.baseline_tearing)


def _download_zip(run: CaseRunResult) -> None:
    import streamlit as st

    payload = build_audit_zip(run)
    case_id = run.case.case_id
    st.download_button(
        label=DOWNLOAD_ZIP,
        data=payload,
        file_name=f"{case_id}_{run.objective}_relatorio.zip",
        mime="application/zip",
    )


def _diagnostic_tab(advanced: bool, time_limit: float) -> None:
    import streamlit as st

    preset = st.selectbox(PRESET_LABEL, [PRESET_IDEAL, PRESET_REAL], key="diag_preset")
    yaml_text: Optional[str] = None
    if advanced:
        upload = st.file_uploader(UPLOAD_YAML, type=["yaml", "yml"], key="diag_upload")
        if upload is not None:
            yaml_text = upload.getvalue().decode("utf-8")
        else:
            default_path = PRESET_PATHS[preset]
            yaml_text = default_path.read_text(encoding="utf-8")
            yaml_text = st.text_area(YAML_EDITOR, value=yaml_text, height=200, key="diag_yaml")

    if st.button(RUN_DIAGNOSTIC, type="primary", key="diag_run_btn"):
        try:
            if advanced and yaml_text:
                case_def = _load_yaml_text(yaml_text, preset)
                if case_def.analysis.objective != "classify":
                    case_def = replace(
                        case_def,
                        analysis=AnalysisConfig(
                            objective="classify",
                            criterion=case_def.analysis.criterion,
                            repair=case_def.analysis.repair,
                        ),
                    )
            else:
                case_def = _load_preset(PRESET_PATHS[preset])
            case_def = replace(
                case_def,
                solver=replace(case_def.solver, time_limit_s=time_limit),
            )
            with st.spinner(SPINNER_DIAGNOSTIC):
                result = run_case(case_def)
            st.session_state["diag_result"] = result
        except (ValueError, yaml.YAMLError) as exc:
            st.error(f"{ERROR_INVALID_CASE} ({exc})")
        except Exception as exc:
            st.error(f"{ERROR_RUN_FAILED} ({exc})")

    stored = st.session_state.get("diag_result")
    if isinstance(stored, CaseRunResult):
        _render_classification(stored, advanced)
        _download_zip(stored)


def _repair_tab(advanced: bool, time_limit: float) -> None:
    import streamlit as st

    st.info(REPAIR_BASELINE_INFO.format(preset=PRESET_REPAIR))
    yaml_text: Optional[str] = None
    if advanced:
        upload = st.file_uploader(UPLOAD_YAML, type=["yaml", "yml"], key="repair_upload")
        if upload is not None:
            yaml_text = upload.getvalue().decode("utf-8")
        else:
            default_path = PRESET_PATHS[PRESET_REPAIR]
            yaml_text = default_path.read_text(encoding="utf-8")
            yaml_text = st.text_area(
                YAML_EDITOR, value=yaml_text, height=200, key="repair_yaml"
            )

    if st.button(RUN_REPAIR, type="primary", key="repair_run_btn"):
        try:
            if advanced and yaml_text:
                case_def = _load_yaml_text(yaml_text, PRESET_REPAIR)
                if case_def.analysis.objective != "min_repair":
                    case_def = replace(
                        case_def,
                        analysis=AnalysisConfig(
                            objective="min_repair",
                            criterion=case_def.analysis.criterion,
                            repair=case_def.analysis.repair,
                        ),
                    )
            else:
                case_def = _load_preset(PRESET_PATHS[PRESET_REPAIR])
            case_def = replace(
                case_def,
                solver=replace(case_def.solver, time_limit_s=time_limit),
            )
            with st.spinner(SPINNER_REPAIR):
                result = run_case(case_def)
            st.session_state["repair_result"] = result
        except (ValueError, yaml.YAMLError) as exc:
            st.error(f"{ERROR_INVALID_CASE} ({exc})")
        except Exception as exc:
            st.error(f"{ERROR_RUN_FAILED} ({exc})")

    stored = st.session_state.get("repair_result")
    if isinstance(stored, CaseRunResult):
        _render_repair(stored, advanced)
        _download_zip(stored)


def _render_milp(run: CaseRunResult, advanced: bool) -> None:
    import streamlit as st

    view = present_milp(run)
    if run.milp_summary is not None and run.milp_summary.status in (
        "optimal",
        "feasible",
    ):
        st.success(view.headline)
    elif run.milp_summary is not None and run.milp_summary.status == "infeasible":
        st.warning(view.headline)
    elif run.milp_summary is not None and run.milp_summary.status == "not_optimal":
        st.error(view.headline)
    else:
        st.info(view.headline)
    render_milp_summary(view, advanced)


def _milp_tab(advanced: bool) -> None:
    import streamlit as st

    st.warning(MILP_WARNING)
    preset = st.selectbox(
        PRESET_LABEL,
        [
            PRESET_MILP_GLOBAL,
            PRESET_MILP_VERIFY_REAL,
            PRESET_MILP_VERIFY_IDEAL,
            PRESET_MILP_REPAIR,
        ],
        key="milp_preset",
    )
    hint = MILP_PRESET_HINTS.get(preset)
    if hint:
        st.info(hint)
    yaml_text: Optional[str] = None
    if advanced:
        upload = st.file_uploader(UPLOAD_YAML, type=["yaml", "yml"], key="milp_upload")
        if upload is not None:
            yaml_text = upload.getvalue().decode("utf-8")
        else:
            default_path = PRESET_PATHS[preset]
            yaml_text = default_path.read_text(encoding="utf-8")
            yaml_text = st.text_area(YAML_EDITOR, value=yaml_text, height=200, key="milp_yaml")

    if st.button(RUN_MILP, type="primary", key="milp_run_btn"):
        try:
            if advanced and yaml_text:
                case_def = _load_yaml_text(yaml_text, preset)
            else:
                case_def = _load_preset(PRESET_PATHS[preset])
            with st.spinner(SPINNER_MILP):
                result = run_case(case_def)
            st.session_state["milp_result"] = result
        except (ValueError, yaml.YAMLError) as exc:
            st.error(f"{ERROR_INVALID_CASE} ({exc})")
        except Exception as exc:
            st.error(f"{ERROR_RUN_FAILED} ({exc})")

    stored = st.session_state.get("milp_result")
    if isinstance(stored, CaseRunResult):
        _render_milp(stored, advanced)
        _download_zip(stored)


def run_app() -> None:
    """Streamlit application entry (called by streamlit run)."""
    import streamlit as st

    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    with st.sidebar:
        st.header(SIDEBAR_HEADER)
        advanced = st.checkbox(ADVANCED_MODE, value=False)
        time_limit = st.slider(SIDEBAR_TIME_LIMIT, min_value=10, max_value=120, value=60)
        st.markdown("---")
        with st.expander(ABOUT_TITLE, expanded=False):
            st.write(ABOUT_TEXT)

    st.info(CRITERION_LINE)
    tab_diag, tab_repair, tab_milp = st.tabs([TAB_DIAGNOSTIC, TAB_REPAIR, TAB_MILP])
    with tab_diag:
        _diagnostic_tab(advanced, float(time_limit))
    with tab_repair:
        _repair_tab(advanced, float(time_limit))
    with tab_milp:
        _milp_tab(advanced)


def main() -> None:
    """Console entry point: launch Streamlit on this module."""
    import streamlit.web.cli as stcli

    app_path = Path(__file__).resolve()
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=true",
    ]
    sys.exit(stcli.main())


if __name__ == "__main__":
    run_app()

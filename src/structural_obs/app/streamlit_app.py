#!/usr/bin/env python3
"""Streamlit UI: simple Portuguese labels for classify and min_repair."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from structural_obs import PROJECT_ROOT
from structural_obs.app.bundle import build_audit_zip
from structural_obs.app.presenters import (
    present_classification,
    present_repair,
    repair_option_table_rows,
)
from structural_obs.app.ui_labels import (
    ABOUT_TEXT,
    ABOUT_TITLE,
    ADVANCED_MODE,
    APP_SUBTITLE,
    APP_TITLE,
    CARD_CALCULABLE,
    CARD_MEASURED,
    CARD_NOT_CALCULABLE,
    CARD_TO_ADD,
    CARD_TOTAL_AFTER,
    COL_INSTALL,
    COL_OPTION,
    COL_RESULT,
    COL_STATUS,
    COL_TAG,
    COMPUTES_ALL_QUESTION,
    CRITERION_LINE,
    DOWNLOAD_ZIP,
    ERROR_INVALID_CASE,
    ERROR_RUN_FAILED,
    NO,
    PRESET_IDEAL,
    PRESET_LABEL,
    PRESET_REAL,
    PRESET_REPAIR,
    RUN_DIAGNOSTIC,
    RUN_REPAIR,
    SECTION_CALCULATED,
    SECTION_INSTALL_OPTIONS,
    SECTION_NOT_CALCULATED,
    SECTION_OPEN_BALANCES,
    TAB_DIAGNOSTIC,
    TAB_REPAIR,
    TECH_C_CL,
    TECH_C_DIR,
    TECH_C_EXT,
    TECH_SOLVER,
    UPLOAD_YAML,
    YES,
    YAML_EDITOR,
)
from structural_obs.toolkit.schemas.case_schema import AnalysisConfig
from structural_obs.toolkit.services.classify_service import CaseRunResult, run_case
from structural_obs.toolkit.schemas.loaders import load_case

CASES_DIR = PROJECT_ROOT / "cases"

PRESET_PATHS: dict[str, Path] = {
    PRESET_IDEAL: CASES_DIR / "urs_pdf_ideal.yaml",
    PRESET_REAL: CASES_DIR / "urs_pdf_real.yaml",
    PRESET_REPAIR: CASES_DIR / "urs_pdf_repair.yaml",
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
    c1, c2, c3 = st.columns(3)
    c1.metric(CARD_CALCULABLE, f"{view.calculable} de {view.total}")
    c2.metric(CARD_NOT_CALCULABLE, view.not_calculable)
    c3.metric(CARD_MEASURED, view.measured_count)
    st.write(f"{COMPUTES_ALL_QUESTION} **{YES if view.computes_all else NO}**")
    st.caption(view.solver_label)

    with st.expander(SECTION_CALCULATED, expanded=False):
        if view.calculable_tags:
            st.write(", ".join(view.calculable_tags))
        else:
            st.write("-")

    with st.expander(SECTION_NOT_CALCULATED, expanded=bool(view.not_calculable_tags)):
        if view.not_calculable_tags:
            st.write(", ".join(view.not_calculable_tags))
        else:
            st.write("-")

    with st.expander(SECTION_OPEN_BALANCES, expanded=bool(view.open_balance_tags)):
        if view.open_balance_tags:
            st.write(", ".join(view.open_balance_tags))
        else:
            st.write("-")

    if advanced and run.classification is not None and run.tearing_result is not None:
        st.subheader("Detalhes tecnicos")
        summary = run.classification
        tr = run.tearing_result
        t1, t2, t3, t4 = st.columns(4)
        t1.metric(TECH_C_CL, f"{summary.c_closed}/{summary.total_variables}")
        t2.metric(TECH_C_EXT, f"{summary.c_external}/{summary.total_variables}")
        t3.metric(TECH_C_DIR, f"{summary.c_direct}/{summary.total_variables}")
        t4.metric(TECH_SOLVER, summary.solver_status)
        df = pd.DataFrame(
            [{"tag": r["tag"], "status": r["status"]} for r in view.variable_rows]
        )
        df.columns = [COL_TAG, COL_STATUS]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.json(
            {
                "open_tears": tr.tears_open,
                "effective_indeterminate": tr.effective_indeterminate,
            }
        )


def _render_repair(run: CaseRunResult, advanced: bool) -> None:
    import streamlit as st

    view = present_repair(run)
    if view.minimum_additions is None:
        st.warning(view.headline)
    else:
        st.success(view.headline)

    c1, c2, c3 = st.columns(3)
    c1.metric(CARD_MEASURED, view.base_measured_count)
    if view.minimum_additions is not None:
        c2.metric(CARD_TO_ADD, view.minimum_additions)
        c3.metric(CARD_TOTAL_AFTER, view.total_after or "-")
    else:
        c2.metric(CARD_TO_ADD, "-")
        c3.metric(
            CARD_CALCULABLE,
            f"{view.baseline_calculable} de {view.baseline_total}",
        )
    st.caption(view.solver_label)

    if view.options:
        st.subheader(SECTION_INSTALL_OPTIONS)
        table = repair_option_table_rows(view.options)
        df = pd.DataFrame(table)
        df.columns = [COL_OPTION, COL_INSTALL, COL_RESULT]
        st.dataframe(df, use_container_width=True, hide_index=True)

    if advanced and run.repair_result is not None:
        st.subheader("Detalhes tecnicos")
        st.write(
            {
                "minimum_additions": run.repair_result.minimum_additions,
                "evaluated_count": len(run.repair_result.all_evaluated),
                "candidate_pool": list(run.repair_result.candidate_pool),
            }
        )


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

    if st.button(RUN_DIAGNOSTIC, type="primary", key="diag_run"):
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
            with st.spinner("Analisando medidas..."):
                run = run_case(case_def)
            st.session_state["diag_run"] = run
        except (ValueError, yaml.YAMLError) as exc:
            st.error(f"{ERROR_INVALID_CASE} ({exc})")
        except Exception as exc:
            st.error(f"{ERROR_RUN_FAILED} ({exc})")

    if "diag_run" in st.session_state:
        run: CaseRunResult = st.session_state["diag_run"]
        _render_classification(run, advanced)
        _download_zip(run)


def _repair_tab(advanced: bool, time_limit: float) -> None:
    import streamlit as st

    st.info(
        f"Situacao de partida: URS real com 22 medidores "
        f"({PRESET_REPAIR})."
    )
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

    if st.button(RUN_REPAIR, type="primary", key="repair_run"):
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
            with st.spinner("Buscando medidores faltantes..."):
                run = run_case(case_def)
            st.session_state["repair_run"] = run
        except (ValueError, yaml.YAMLError) as exc:
            st.error(f"{ERROR_INVALID_CASE} ({exc})")
        except Exception as exc:
            st.error(f"{ERROR_RUN_FAILED} ({exc})")

    if "repair_run" in st.session_state:
        run: CaseRunResult = st.session_state["repair_run"]
        _render_repair(run, advanced)
        _download_zip(run)


def run_app() -> None:
    """Streamlit application entry (called by streamlit run)."""
    import streamlit as st

    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    with st.sidebar:
        st.header("Configuracao")
        advanced = st.checkbox(ADVANCED_MODE, value=False)
        time_limit = st.slider("Tempo maximo (s)", min_value=10, max_value=120, value=60)
        st.markdown("---")
        with st.expander(ABOUT_TITLE, expanded=False):
            st.write(ABOUT_TEXT)

    st.info(CRITERION_LINE)
    tab_diag, tab_repair = st.tabs([TAB_DIAGNOSTIC, TAB_REPAIR])
    with tab_diag:
        _diagnostic_tab(advanced, float(time_limit))
    with tab_repair:
        _repair_tab(advanced, float(time_limit))


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

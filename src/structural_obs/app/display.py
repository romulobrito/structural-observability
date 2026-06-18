#!/usr/bin/env python3
"""Shared Streamlit rendering helpers for classification and repair views."""

from __future__ import annotations

from typing import Optional, Sequence

import pandas as pd

from structural_obs.app.presenters import ClassificationView, MilpView, RepairView, repair_option_table_rows
from structural_obs.app.ui_labels import (
    CARD_CALCULABLE,
    CARD_DIRECT,
    CARD_EXTERNAL_REACH,
    CARD_GRANDEZAS,
    CARD_INDETERMINATE,
    CARD_INFERRED,
    CARD_MEASURED,
    CARD_MILP_INFERRED,
    CARD_MILP_REDUNDANCY,
    CARD_MILP_SENSORS,
    CARD_MILP_TEARING,
    CARD_NOT_CALCULABLE,
    CARD_OPEN_TEARS,
    CARD_TO_ADD,
    CARD_TOTAL_AFTER,
    COL_INDETERMINATE,
    COL_INSTALL,
    COL_OPEN_TEARS,
    COL_OPTION,
    COL_RESULT,
    COL_STATUS,
    COL_TAG,
    COL_TOTAL_MEASURED,
    COMPUTES_ALL_QUESTION,
    HELP_CALCULABLE,
    HELP_COMPUTES_ALL,
    HELP_DIRECT,
    HELP_EXTERNAL_REACH,
    HELP_GRANDEZAS,
    HELP_INDETERMINATE,
    HELP_INFERRED,
    HELP_MEASURED,
    HELP_NOT_CALCULABLE,
    HELP_MILP_INFERRED,
    HELP_MILP_MODE,
    HELP_MILP_REDUNDANCY,
    HELP_MILP_SENSORS,
    HELP_MILP_STATUS,
    HELP_MILP_TEARING,
    HELP_OPEN_TEARS,
    HELP_TECH_C_CL,
    HELP_TECH_C_DIR,
    HELP_TECH_C_EXT,
    HELP_TECH_EQUATIONS,
    HELP_TECH_INDETERMINATE,
    HELP_TECH_OPEN_TEARS,
    HELP_TECH_SOLVER,
    HELP_AUTO_POOL,
    HELP_REPAIR_CANDIDATES,
    HELP_TO_ADD,
    HELP_TOTAL_AFTER,
    NO,
    SECTION_AUTO_POOL,
    SECTION_BY_STATUS,
    SECTION_INDETERMINATE,
    SECTION_INFERRED,
    SECTION_INSTALL_OPTIONS,
    SECTION_MEASURED,
    SECTION_MILP_ADDITIONS,
    SECTION_MILP_CONFLICTS,
    SECTION_MILP_INFERRED,
    SECTION_MILP_MEASURED,
    SECTION_MILP_MODE,
    SECTION_MILP_TEARING_AUDIT,
    SECTION_OPEN_BALANCES,
    SECTION_REPAIR_BEFORE,
    SECTION_REPAIR_CANDIDATES,
    SECTION_VARIABLE_TABLE,
    TECH_C_CL,
    TECH_C_DIR,
    TECH_C_EXT,
    TECH_DETAILS_HEADER,
    TECH_EQUATIONS,
    TECH_INDETERMINATE,
    TECH_OPEN_TEARS,
    TECH_SOLVER,
    YES,
)
from structural_obs.tearing.core import TearingResult


def _tag_list(tags: Sequence[str]) -> str:
    if not tags:
        return "—"
    return ", ".join(tags)


def _render_computes_all_line(computes_all: bool) -> None:
    """Render 'Calcula tudo?' with a help popover (no st.tooltip on Streamlit 1.33)."""
    import streamlit as st

    left, right = st.columns([11, 1])
    with left:
        st.write(f"{COMPUTES_ALL_QUESTION} **{YES if computes_all else NO}**")
    with right:
        with st.popover("?"):
            st.write(HELP_COMPUTES_ALL)


def render_classification_summary(view: ClassificationView) -> None:
    """Render KPI cards for a classification view."""
    import streamlit as st

    m = view.metrics
    _render_computes_all_line(m.computes_all)
    st.caption(m.solver_label)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(CARD_CALCULABLE, f"{m.calculable} de {m.total}", help=HELP_CALCULABLE)
    c2.metric(CARD_INFERRED, m.inferred_count, help=HELP_INFERRED)
    c3.metric(CARD_INDETERMINATE, m.indeterminate_count, help=HELP_INDETERMINATE)
    c4.metric(CARD_MEASURED, m.measured_count, help=HELP_MEASURED)

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(CARD_NOT_CALCULABLE, m.not_calculable, help=HELP_NOT_CALCULABLE)
    c6.metric(CARD_OPEN_TEARS, m.open_tears_count, help=HELP_OPEN_TEARS)
    c7.metric(
        CARD_EXTERNAL_REACH,
        f"{m.external_reach} de {m.total}",
        help=HELP_EXTERNAL_REACH,
    )
    c8.metric(
        CARD_DIRECT,
        f"{m.direct_count} de {m.total}",
        help=HELP_DIRECT,
    )


def render_classification_details(
    view: ClassificationView,
    advanced: bool,
    tearing_result: Optional[TearingResult],
) -> None:
    """Render tables and grouped lists for one classification view."""
    import streamlit as st

    st.subheader(SECTION_VARIABLE_TABLE)
    df = pd.DataFrame([{"tag": r["tag"], "status": r["status"]} for r in view.variable_rows])
    df.columns = [COL_TAG, COL_STATUS]
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader(SECTION_BY_STATUS)
    for group in view.status_groups:
        with st.expander(f"{group.label} ({len(group.tags)})", expanded=False):
            st.write(_tag_list(group.tags))

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**{SECTION_MEASURED}** ({len(view.measured_tags)})")
        st.write(_tag_list(view.measured_tags))
        st.markdown(f"**{SECTION_INFERRED}** ({len(view.inferred_tags)})")
        st.write(_tag_list(view.inferred_tags))
    with col_b:
        st.markdown(f"**{SECTION_INDETERMINATE}** ({len(view.not_calculable_tags)})")
        st.write(_tag_list(view.not_calculable_tags))
        st.markdown(f"**{SECTION_OPEN_BALANCES}** ({len(view.open_balance_tags)})")
        st.write(_tag_list(view.open_balance_tags))

    if advanced and tearing_result is not None:
        st.subheader(TECH_DETAILS_HEADER)
        t1, t2, t3, t4 = st.columns(4)
        t1.metric(
            TECH_C_CL,
            f"{view.metrics.calculable}/{view.metrics.total}",
            help=HELP_TECH_C_CL,
        )
        t2.metric(
            TECH_C_EXT,
            f"{view.metrics.external_reach}/{view.metrics.total}",
            help=HELP_TECH_C_EXT,
        )
        t3.metric(
            TECH_C_DIR,
            f"{view.metrics.direct_count}/{view.metrics.total}",
            help=HELP_TECH_C_DIR,
        )
        phases = tearing_result.status_by_phase
        solver_status = phases.get("phase3") or next(iter(phases.values()), "—")
        t4.metric(TECH_SOLVER, solver_status, help=HELP_TECH_SOLVER)

        t5, t6, t7 = st.columns(3)
        t5.metric(TECH_OPEN_TEARS, view.metrics.open_tears_count, help=HELP_TECH_OPEN_TEARS)
        t6.metric(
            TECH_INDETERMINATE,
            view.metrics.indeterminate_count,
            help=HELP_TECH_INDETERMINATE,
        )
        t7.metric(TECH_EQUATIONS, tearing_result.total_equations, help=HELP_TECH_EQUATIONS)

        if tearing_result.tear_pairs:
            tear_rows = [
                {
                    COL_TAG: var,
                    "Equação": eq,
                    COL_STATUS: (
                        "aberto" if var in tearing_result.tears_open else "fechado"
                    ),
                }
                for eq, var in tearing_result.tear_pairs
            ]
            st.dataframe(pd.DataFrame(tear_rows), use_container_width=True, hide_index=True)


def render_repair_summary(view: RepairView) -> None:
    """Render repair KPI row, candidates and installation options."""
    import streamlit as st

    st.caption(view.solver_label)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(CARD_MEASURED, view.base_measured_count, help=HELP_MEASURED)
    c2.metric(
        CARD_TO_ADD,
        view.minimum_additions if view.minimum_additions is not None else "—",
        help=HELP_TO_ADD,
    )
    c3.metric(
        CARD_TOTAL_AFTER,
        view.total_after if view.total_after is not None else "—",
        help=HELP_TOTAL_AFTER,
    )
    c4.metric(CARD_GRANDEZAS, view.baseline.metrics.total, help=HELP_GRANDEZAS)

    pool_title = SECTION_AUTO_POOL if view.automatic_pool else SECTION_REPAIR_CANDIDATES
    pool_help = HELP_AUTO_POOL if view.automatic_pool else HELP_REPAIR_CANDIDATES
    left, right = st.columns([11, 1])
    with left:
        st.markdown(f"**{pool_title}** ({len(view.candidates)})")
    with right:
        with st.popover("?"):
            st.write(pool_help)
    st.write(_tag_list(view.candidates))

    if view.options:
        st.subheader(SECTION_INSTALL_OPTIONS)
        table = repair_option_table_rows(view.options)
        df = pd.DataFrame(table)
        df.columns = [
            COL_OPTION,
            COL_INSTALL,
            COL_TOTAL_MEASURED,
            COL_RESULT,
            COL_INDETERMINATE,
            COL_OPEN_TEARS,
        ]
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_milp_summary(view: MilpView, advanced: bool) -> None:
    """Render MILP placement summary and optional tearing audit."""
    import streamlit as st

    m1, m2 = st.columns(2)
    m1.metric(SECTION_MILP_MODE, view.mode_label, help=HELP_MILP_MODE)
    m2.metric("Status MILP", view.status, help=HELP_MILP_STATUS)
    st.caption(f"Solver: {view.solver_name}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(CARD_MILP_SENSORS, view.sensor_count, help=HELP_MILP_SENSORS)
    c2.metric(CARD_MILP_INFERRED, len(view.inferred_tags), help=HELP_MILP_INFERRED)
    c3.metric(
        CARD_MILP_REDUNDANCY,
        f"{view.redundancy_cost:.1f}",
        help=HELP_MILP_REDUNDANCY,
    )
    if view.tearing_c_closed is not None and view.tearing_total is not None:
        c4.metric(
            CARD_MILP_TEARING,
            f"{view.tearing_c_closed}/{view.tearing_total}",
            help=HELP_MILP_TEARING,
        )
    else:
        c4.metric(CARD_MILP_TEARING, "—", help=HELP_MILP_TEARING)

    if view.measured_tags:
        st.markdown(f"**{SECTION_MILP_MEASURED}** ({len(view.measured_tags)})")
        st.write(_tag_list(view.measured_tags))
    if view.inferred_tags:
        st.markdown(f"**{SECTION_MILP_INFERRED}** ({len(view.inferred_tags)})")
        st.write(_tag_list(view.inferred_tags))

    if view.additions_tags:
        st.markdown(f"**{SECTION_MILP_ADDITIONS}** ({len(view.additions_tags)})")
        st.write(_tag_list(view.additions_tags))

    if view.conflicts:
        st.subheader(SECTION_MILP_CONFLICTS)
        for issue in view.conflicts:
            st.write(f"- {issue}")

    if view.classification is not None and view.tearing_result is not None:
        st.subheader(SECTION_MILP_TEARING_AUDIT)
        render_classification_summary(view.classification)
        if advanced:
            render_classification_details(
                view.classification,
                advanced,
                view.tearing_result,
            )

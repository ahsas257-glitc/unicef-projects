from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from src.config import (
    APP_TITLE,
    APP_SUBTITLE,
    PROJECTS,
    SCOPES,
    DEFAULT_YEAR,
)

from src.google_sheets import load_google_sheet
from src.data_model import build_master_dataset

from src.analytics import (
    apply_filters,
    portfolio_summary,
    project_summary,
    monthly_summary,
    province_summary,
    rejection_summary,
    staff_summary,
    quality_summary,
    vt_tool_summary,
    data_quality_summary,
    executive_insights,
    project_specific_breakdowns,
    district_summary,
    qc_reviewer_summary,
    calendar_heatmap_data,
    province_quality_index,
)

from src.charts import (
    fig_scope_completion,
    fig_status_mix,
    fig_monthly_trend,
    fig_project_health_matrix,
    fig_province_status,
    fig_rejection_pareto,
    fig_vt_tool_bubble,
    fig_staff_scatter,
    fig_category_bar,
    fig_sunburst,
    fig_quality_components,
    fig_project_radar,
    fig_treemap,
    fig_calendar_heatmap,
    fig_waterfall,
    fig_funnel,
    fig_speedometer,
    fig_province_quality_scatter,
    fig_qc_reviewer,
)

from src.ui import (
    inject_css,
    force_dark_mode,
    hero,
    metric_card,
    section_header,
    insight_card,
    pill,
    footer,
    show_empty_state,
    panel_title,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="UNICEF Portfolio Intelligence",
    page_icon="◈",
    layout="wide",

    # Sidebar initially visible,
    # but user can open / close it.
    initial_sidebar_state="expanded",

    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    },
)


# ============================================================
# FRONTEND / DARK MODE
# ============================================================

force_dark_mode()
inject_css()


# ============================================================
# PLOTLY RENDERER
# ============================================================

def render_chart(
    figure,
    key: str,
    *,
    modebar: bool = False,
) -> None:
    """
    Render Plotly figures with a guaranteed unique Streamlit key.
    """

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displayModeBar": modebar,
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": False,
        },
        key=key,
    )


# ============================================================
# CONTEXT BAR
# ============================================================

def render_context_bar(
    year: int,
    project: str,
    latest_date: str,
    row_count: int,
    refreshed: str,
) -> None:
    """
    Render dashboard context badges with st.html() instead of
    st.markdown(), preventing HTML from appearing as raw text.
    """

    html = (
        '<div class="context-strip">'
        f'{pill(f"Year {year}")}'
        f'{pill(project)}'
        f'{pill(f"Latest data: {latest_date}")}'
        f'{pill(f"Rows in current view: {row_count:,}")}'
        f'{pill(f"Refreshed: {refreshed}")}'
        '</div>'
    )

    st.html(html)


# ============================================================
# HERO
# ============================================================

hero(
    title=APP_TITLE,
    subtitle=APP_SUBTITLE,
    badge="LIVE • GOOGLE SHEETS • PUBLIC INTELLIGENCE",
)


# ============================================================
# SIDEBAR HEADER
# ============================================================

with st.sidebar:

    st.markdown("### COMMAND CENTER")

    st.caption(
        "Live analytics powered exclusively by the internal "
        "project tabs of the connected Google Sheet."
    )

    if st.button(
        "↻ Refresh live data",
        use_container_width=True,
        type="primary",
        key="sidebar_refresh_live_data",
    ):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")


# ============================================================
# LOAD GOOGLE SHEET
# ============================================================

try:

    sheet_frames, source_meta = load_google_sheet()

except Exception as exc:

    st.error(
        "The dashboard could not connect to Google Sheets."
    )

    st.code(str(exc))

    st.info(
        "Check Streamlit Cloud → Settings → Secrets, "
        "then make sure the Google Sheet is shared with "
        "the service-account email as Viewer."
    )

    st.stop()


# ============================================================
# BUILD MASTER DATASET
# ============================================================

master, model_meta = build_master_dataset(
    sheet_frames
)


if master.empty:

    show_empty_state(
        "No usable records were found.",
        "Check the project tabs, column headers and source data.",
    )

    st.stop()


# ============================================================
# AVAILABLE YEARS
# ============================================================

years = sorted(
    int(value)
    for value in master["year"].dropna().unique()
)


if not years:
    years = [DEFAULT_YEAR]


default_year = (
    DEFAULT_YEAR
    if DEFAULT_YEAR in years
    else max(years)
)


# ============================================================
# URL PROJECT PARAMETER
# ============================================================

query_project = None


try:
    query_project = st.query_params.get("project")

except Exception:
    query_project = None


project_options = [
    "All Projects",
    *PROJECTS,
]


default_project_index = 0


if query_project in PROJECTS:

    default_project_index = (
        project_options.index(
            query_project
        )
    )


# ============================================================
# GLOBAL FILTERS
# ============================================================

with st.sidebar:

    st.markdown(
        "#### GLOBAL FILTERS"
    )


    selected_year = st.selectbox(
        "Reporting year",
        years,
        index=years.index(
            default_year
        ),
        key="filter_reporting_year",
    )


    selected_project = st.selectbox(
        "Project view",
        project_options,
        index=default_project_index,
        key="filter_project_view",
    )


    # --------------------------------------------------------
    # PROJECT IN URL
    # --------------------------------------------------------

    try:

        if selected_project == "All Projects":

            if "project" in st.query_params:
                del st.query_params["project"]

        else:

            st.query_params["project"] = (
                selected_project
            )

    except Exception:
        pass


    include_undated_vt = st.toggle(
        "Include undated VT KII/FGD in totals",
        value=True,
        help=(
            "Undated KII/FGD records remain in VT totals, "
            "but cannot appear in date-based visualizations."
        ),
        key="filter_include_undated_vt",
    )


# ============================================================
# YEAR FILTER
# ============================================================

year_mask = (
    master["year"]
    .eq(selected_year)
)


if include_undated_vt:

    year_mask |= (
        master["date"].isna()
        & master["project"].eq("VT")
        & master["subsource"].eq(
            "VT KII/FGD"
        )
    )


year_df = (
    master.loc[
        year_mask
    ]
    .copy()
)


# ============================================================
# PROJECT FILTER
# ============================================================

project_df = (
    year_df.copy()
)


if selected_project != "All Projects":

    project_df = (
        project_df[
            project_df[
                "project"
            ].eq(
                selected_project
            )
        ]
        .copy()
    )


# ============================================================
# ADVANCED FILTERS
# ============================================================

with st.sidebar:

    province_values = sorted(
        value
        for value
        in project_df[
            "province"
        ]
        .fillna("")
        .astype(str)
        .unique()
        if (
            value.strip()
            and value != "Unknown"
        )
    )


    selected_provinces = (
        st.multiselect(
            "Province",
            province_values,
            default=[],
            key="filter_province",
        )
    )


    status_values = [
        "Approved",
        "Rejected",
        "Pending",
        "Unreviewed",
    ]


    selected_statuses = (
        st.multiselect(
            "QA status",
            status_values,
            default=status_values,
            key="filter_qa_status",
        )
    )


    tool_values = sorted(
        value
        for value
        in project_df[
            "tool_type"
        ]
        .fillna("")
        .astype(str)
        .unique()
        if (
            value.strip()
            and value != "Unknown"
        )
    )


    selected_tools = (
        st.multiselect(
            "Tool / instrument",
            tool_values,
            default=[],
            key="filter_tool_instrument",
        )
    )


    search_text = (
        st.text_input(
            "Search operational fields",
            placeholder=(
                "Province, district, tool, "
                "rejection reason..."
            ),
            key="filter_search_text",
        )
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = apply_filters(
    project_df,
    provinces=selected_provinces,
    statuses=selected_statuses,
    tools=selected_tools,
    search_text=search_text,
)


# ============================================================
# DASHBOARD CONTEXT
# ============================================================

latest_dated = (
    year_df[
        "date"
    ]
    .dropna()
    .max()
)


if pd.notna(latest_dated):

    latest_date_text = (
        latest_dated.strftime(
            "%d %b %Y"
        )
    )

else:

    latest_date_text = (
        "No dated records"
    )


refresh_text = (
    datetime.now(
        ZoneInfo(
            "Asia/Kabul"
        )
    )
    .strftime(
        "%d %b %Y • %H:%M"
    )
)


# IMPORTANT:
# st.html() is used here instead of st.markdown().
# This fixes the raw <span> HTML appearing on screen.

render_context_bar(
    year=selected_year,
    project=selected_project,
    latest_date=latest_date_text,
    row_count=len(filtered),
    refreshed=refresh_text,
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

(
    tab_overview,
    tab_portfolio,
    tab_project,
    tab_quality,
    tab_geo,
    tab_time,
    tab_explorer,
) = st.tabs(
    [
        "Executive Overview",
        "Portfolio Intelligence",
        "Project Deep Dive",
        "Quality & Risk",
        "Geography",
        "Time Intelligence",
        "Data Explorer",
    ]
)


# ============================================================
# TAB 1
# EXECUTIVE OVERVIEW
# ============================================================

with tab_overview:

    executive_projects = (
        PROJECTS
        if selected_project
        == "All Projects"
        else [
            selected_project
        ]
    )


    summary = (
        portfolio_summary(
            year_df,
            SCOPES,
            projects=executive_projects,
        )
    )


    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    total_scope = int(
        summary[
            "Scope"
        ].sum()
    )


    total_received = int(
        summary[
            "Received"
        ].sum()
    )


    total_approved = int(
        summary[
            "Approved"
        ].sum()
    )


    total_rejected = int(
        summary[
            "Rejected"
        ].sum()
    )


    total_pending = int(
        summary[
            "Pending / Unreviewed"
        ].sum()
    )


    total_remaining = int(
        summary[
            "Remaining"
        ].sum()
    )


    progress = (
        total_approved
        / total_scope
        if total_scope
        else 0
    )


    coverage = (
        total_received
        / total_scope
        if total_scope
        else 0
    )


    approval_rate = (
        total_approved
        / total_received
        if total_received
        else 0
    )


    rejection_rate = (
        total_rejected
        / total_received
        if total_received
        else 0
    )


    reviewed_rate = (
        (
            total_approved
            + total_rejected
        )
        / total_received
        if total_received
        else 0
    )


    backlog_rate = (
        total_pending
        / total_received
        if total_received
        else 0
    )


    # --------------------------------------------------------
    # EXECUTIVE KPIs
    # --------------------------------------------------------

    section_header(
        "Executive Snapshot",
        (
            "A compact management view of delivery, "
            "quality and scope performance"
        ),
    )


    (
        k1,
        k2,
        k3,
        k4,
        k5,
        k6,
    ) = st.columns(6)


    with k1:

        metric_card(
            "Scope",
            f"{total_scope:,}",
            "Configured target",
            "neutral",
        )


    with k2:

        metric_card(
            "Received",
            f"{total_received:,}",
            (
                f"{coverage:.1%} "
                "collection coverage"
            ),
            "blue",
        )


    with k3:

        metric_card(
            "Approved",
            f"{total_approved:,}",
            (
                f"{approval_rate:.1%} "
                "approval rate"
            ),
            "green",
        )


    with k4:

        metric_card(
            "Rejected",
            f"{total_rejected:,}",
            (
                f"{rejection_rate:.1%} "
                "rejection rate"
            ),
            "red",
        )


    with k5:

        metric_card(
            "Pending QA",
            f"{total_pending:,}",
            (
                f"{backlog_rate:.1%} "
                "backlog"
            ),
            "amber",
        )


    with k6:

        metric_card(
            "Completion",
            f"{progress:.1%}",
            (
                f"{total_remaining:,} "
                "remaining"
            ),
            "purple",
        )


    # --------------------------------------------------------
    # TOP VISUALS
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(
        [
            1.2,
            1.0,
            0.9,
        ]
    )


    with c1:

        render_chart(
            fig_scope_completion(
                summary
            ),
            key=(
                "overview_"
                "scope_completion"
            ),
        )


    with c2:

        render_chart(
            fig_status_mix(
                total_approved,
                total_rejected,
                total_pending,
            ),
            key=(
                "overview_"
                "status_mix"
            ),
        )


    with c3:

        render_chart(
            fig_speedometer(
                progress,
                title=(
                    "Portfolio Completion"
                ),
            ),
            key=(
                "overview_"
                "completion_gauge"
            ),
        )


    # --------------------------------------------------------
    # RADAR / DQ
    # --------------------------------------------------------

    c1, c2 = st.columns(
        [
            1.2,
            1,
        ]
    )


    with c1:

        render_chart(
            fig_project_radar(
                summary
            ),
            key=(
                "overview_"
                "project_radar"
            ),
        )


    with c2:

        dq = (
            data_quality_summary(
                year_df,
                selected_year,
            )
        )


        panel_title(
            "Data Quality Signals",
            (
                "Checks that can materially "
                "affect interpretation"
            ),
        )


        d1, d2 = st.columns(
            2
        )


        with d1:

            metric_card(
                "QC Reviewed",
                f"{reviewed_rate:.1%}",
                (
                    "Approved + Rejected "
                    "/ Received"
                ),
                "cyan",
            )


            metric_card(
                "Future-dated",
                (
                    f"{dq['future_dated']:,}"
                ),
                "Dates later than today",
                (
                    "red"
                    if dq[
                        "future_dated"
                    ]
                    else "green"
                ),
            )


        with d2:

            metric_card(
                "Undated VT KII/FGD",
                (
                    f"{dq['undated_vt_kii_fgd']:,}"
                ),
                (
                    "Excluded from "
                    "time charts"
                ),
                "amber",
            )


            metric_card(
                "Missing rejection reason",
                (
                    f"{dq['rejected_missing_reason']:,}"
                ),
                (
                    "Rejected records "
                    "without documented reason"
                ),
                (
                    "red"
                    if dq[
                        "rejected_missing_reason"
                    ]
                    else "green"
                ),
            )


    # --------------------------------------------------------
    # MANAGEMENT INTELLIGENCE
    # --------------------------------------------------------

    section_header(
        "Management Intelligence",
        (
            "Automatic interpretation generated "
            "from the current live portfolio"
        ),
    )


    insights = executive_insights(
        summary,
        year_df,
        selected_year,
    )


    insight_columns = (
        st.columns(
            min(
                3,
                max(
                    1,
                    len(
                        insights
                    ),
                ),
            )
        )
    )


    for index, item in enumerate(
        insights
    ):

        with insight_columns[
            index
            % len(
                insight_columns
            )
        ]:

            insight_card(
                item[
                    "title"
                ],
                item[
                    "text"
                ],
                item[
                    "level"
                ],
            )


    # --------------------------------------------------------
    # HEALTH MATRIX
    # --------------------------------------------------------

    section_header(
        "Portfolio Health Matrix",
        (
            "Completion, QA review, rejection "
            "and backlog in one management surface"
        ),
    )


    render_chart(
        fig_project_health_matrix(
            summary
        ),
        key=(
            "overview_"
            "project_health_matrix"
        ),
    )


# ============================================================
# TAB 2
# PORTFOLIO INTELLIGENCE
# ============================================================

with tab_portfolio:

    section_header(
        "Portfolio Intelligence",
        (
            "Advanced comparative analytics "
            "across all projects"
        ),
    )


    all_summary = (
        portfolio_summary(
            year_df,
            SCOPES,
            projects=PROJECTS,
        )
    )


    c1, c2 = st.columns(
        [
            1.15,
            1,
        ]
    )


    with c1:

        render_chart(
            fig_treemap(
                all_summary
            ),
            key=(
                "portfolio_"
                "scope_treemap"
            ),
        )


    with c2:

        render_chart(
            fig_waterfall(
                all_summary
            ),
            key=(
                "portfolio_"
                "remaining_waterfall"
            ),
        )


    c1, c2 = st.columns(
        2
    )


    with c1:

        render_chart(
            fig_funnel(
                all_summary
            ),
            key=(
                "portfolio_"
                "delivery_funnel"
            ),
        )


    with c2:

        render_chart(
            fig_project_health_matrix(
                all_summary
            ),
            key=(
                "portfolio_"
                "health_matrix"
            ),
        )


    # --------------------------------------------------------
    # PROJECT PERFORMANCE TABLE
    # --------------------------------------------------------

    section_header(
        "Project Performance Table",
        (
            "Decision-ready comparison of scope, "
            "collection, approval, rejection and backlog"
        ),
    )


    st.dataframe(
        all_summary.style.format(
            {
                "Scope": "{:,.0f}",
                "Received": "{:,.0f}",
                "Approved": "{:,.0f}",
                "Rejected": "{:,.0f}",
                "Pending / Unreviewed": "{:,.0f}",
                "Remaining": "{:,.0f}",
                "Completion %": "{:.1%}",
                "Collection Coverage %": "{:.1%}",
                "Approval Rate %": "{:.1%}",
                "Rejection Rate %": "{:.1%}",
                "QC Reviewed %": "{:.1%}",
                "Backlog %": "{:.1%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
        height=330,
    )


# ============================================================
# TAB 3
# PROJECT DEEP DIVE
# ============================================================

with tab_project:

    active_project = (
        selected_project
    )


    if (
        active_project
        == "All Projects"
    ):

        active_project = (
            st.selectbox(
                (
                    "Choose a project "
                    "for the deep dive"
                ),
                PROJECTS,
                key=(
                    "deep_dive_"
                    "project_selector"
                ),
            )
        )


    deep_df = (
        year_df[
            year_df[
                "project"
            ].eq(
                active_project
            )
        ]
        .copy()
    )


    psummary = (
        project_summary(
            deep_df,
            active_project,
            SCOPES.get(
                active_project,
                0,
            ),
        )
    )


    section_header(
        (
            f"{active_project} "
            "Deep Dive"
        ),
        (
            "A complete project-level "
            "command dashboard"
        ),
    )


    # --------------------------------------------------------
    # PROJECT KPI CARDS
    # --------------------------------------------------------

    (
        k1,
        k2,
        k3,
        k4,
        k5,
        k6,
    ) = st.columns(
        6
    )


    with k1:

        metric_card(
            "Received",
            (
                f"{psummary['Received']:,}"
            ),
            (
                f"{psummary['Collection Coverage %']:.1%} "
                "of scope"
            ),
            "blue",
        )


    with k2:

        metric_card(
            "Approved",
            (
                f"{psummary['Approved']:,}"
            ),
            (
                f"{psummary['Approval Rate %']:.1%} "
                "approval"
            ),
            "green",
        )


    with k3:

        metric_card(
            "Rejected",
            (
                f"{psummary['Rejected']:,}"
            ),
            (
                f"{psummary['Rejection Rate %']:.1%} "
                "rejected"
            ),
            "red",
        )


    with k4:

        metric_card(
            "Pending",
            (
                f"{psummary['Pending / Unreviewed']:,}"
            ),
            (
                f"{psummary['Backlog %']:.1%} "
                "backlog"
            ),
            "amber",
        )


    with k5:

        metric_card(
            "Remaining",
            (
                f"{psummary['Remaining']:,}"
            ),
            (
                f"{psummary['Completion %']:.1%} "
                "complete"
            ),
            "purple",
        )


    with k6:

        metric_card(
            "Health",
            psummary[
                "Health Flag"
            ],
            psummary[
                "Priority Action"
            ],
            "cyan",
        )


    if deep_df.empty:

        show_empty_state(
            (
                "No records in this "
                "project for the selected year."
            ),
            (
                "Change the year "
                "or project filter."
            ),
        )

    else:

        # ----------------------------------------------------
        # MONTHLY
        # ----------------------------------------------------

        monthly = (
            monthly_summary(
                deep_df,
                selected_year,
            )
        )


        c1, c2 = st.columns(
            [
                1.35,
                1,
            ]
        )


        with c1:

            render_chart(
                fig_monthly_trend(
                    monthly,
                    title=(
                        f"{active_project} "
                        "Monthly Trend"
                    ),
                ),
                key=(
                    "project_"
                    f"{active_project}_"
                    "monthly_trend"
                ),
            )


        with c2:

            render_chart(
                fig_speedometer(
                    psummary[
                        "Completion %"
                    ],
                    title=(
                        f"{active_project} "
                        "Completion"
                    ),
                ),
                key=(
                    "project_"
                    f"{active_project}_"
                    "completion_gauge"
                ),
            )


        # ----------------------------------------------------
        # PROVINCES / REJECTION
        # ----------------------------------------------------

        c1, c2 = st.columns(
            2
        )


        with c1:

            project_provinces = (
                province_summary(
                    deep_df
                )
                .head(
                    18
                )
            )


            render_chart(
                fig_province_status(
                    project_provinces,
                    title=(
                        f"{active_project} "
                        "by Province"
                    ),
                ),
                key=(
                    "project_"
                    f"{active_project}_"
                    "province_status"
                ),
            )


        with c2:

            project_reasons = (
                rejection_summary(
                    deep_df,
                    top_n=12,
                )
            )


            render_chart(
                fig_rejection_pareto(
                    project_reasons,
                    title=(
                        f"{active_project} "
                        "Rejection Pareto"
                    ),
                ),
                key=(
                    "project_"
                    f"{active_project}_"
                    "rejection_pareto"
                ),
            )


        # ----------------------------------------------------
        # PROJECT-SPECIFIC BREAKDOWN
        # ----------------------------------------------------

        project_breakdowns = (
            project_specific_breakdowns(
                deep_df,
                active_project,
            )
        )


        section_header(
            "Project-Specific Intelligence",
            (
                "Visualizations adapt to "
                "the structure of each project"
            ),
        )


        # ====================================================
        # VT
        # ====================================================

        if active_project == "VT":

            vt_summary = (
                vt_tool_summary(
                    deep_df
                )
            )


            c1, c2 = st.columns(
                [
                    1.1,
                    1,
                ]
            )


            with c1:

                render_chart(
                    fig_vt_tool_bubble(
                        vt_summary
                    ),
                    key=(
                        "project_vt_"
                        "tool_risk_map"
                    ),
                )


            with c2:

                render_chart(
                    fig_category_bar(
                        project_breakdowns.get(
                            "tool"
                        ),
                        "Tool",
                        "Records",
                        (
                            "VT Tool "
                            "Distribution"
                        ),
                    ),
                    key=(
                        "project_vt_"
                        "tool_distribution"
                    ),
                )


            st.dataframe(
                vt_summary.style.format(
                    {
                        "Approval Rate %": "{:.1%}",
                        "Rejection Rate %": "{:.1%}",
                        "QC Reviewed %": "{:.1%}",
                        "Backlog %": "{:.1%}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


        # ====================================================
        # MORAA
        # ====================================================

        elif active_project == "Moraa":

            c1, c2 = st.columns(
                [
                    1.15,
                    1,
                ]
            )


            with c1:

                render_chart(
                    fig_sunburst(
                        project_breakdowns.get(
                            "sunburst"
                        ),
                        "Phase",
                        "Discipline",
                        "Status",
                    ),
                    key=(
                        "project_moraa_"
                        "sunburst"
                    ),
                )


            with c2:

                render_chart(
                    fig_category_bar(
                        project_breakdowns.get(
                            "discipline"
                        ),
                        "Discipline",
                        "Records",
                        (
                            "Discipline "
                            "Distribution"
                        ),
                    ),
                    key=(
                        "project_moraa_"
                        "discipline"
                    ),
                )


            c1, c2 = (
                st.columns(
                    2
                )
            )


            with c1:

                render_chart(
                    fig_category_bar(
                        project_breakdowns.get(
                            "phase"
                        ),
                        "Phase",
                        "Records",
                        (
                            "Phase "
                            "Distribution"
                        ),
                    ),
                    key=(
                        "project_moraa_"
                        "phase"
                    ),
                )


            with c2:

                render_chart(
                    fig_category_bar(
                        project_breakdowns.get(
                            "gender"
                        ),
                        "Gender",
                        "Records",
                        (
                            "Gender "
                            "Distribution"
                        ),
                    ),
                    key=(
                        "project_moraa_"
                        "gender"
                    ),
                )


        # ====================================================
        # OTHER PROJECTS
        # ====================================================

        else:

            c1, c2 = st.columns(
                2
            )


            with c1:

                render_chart(
                    fig_category_bar(
                        project_breakdowns.get(
                            "tool"
                        ),
                        "Tool",
                        "Records",
                        (
                            "Tool / "
                            "Instrument Mix"
                        ),
                    ),
                    key=(
                        "project_"
                        f"{active_project}_"
                        "tool_mix"
                    ),
                )


            with c2:

                project_quality = (
                    quality_summary(
                        deep_df
                    )
                )


                render_chart(
                    fig_quality_components(
                        project_quality,
                        title=(
                            "QA Component "
                            "Profile"
                        ),
                    ),
                    key=(
                        "project_"
                        f"{active_project}_"
                        "quality_profile"
                    ),
                )


            project_qc = (
                qc_reviewer_summary(
                    deep_df
                )
            )


            render_chart(
                fig_qc_reviewer(
                    project_qc
                ),
                key=(
                    "project_"
                    f"{active_project}_"
                    "qc_reviewer"
                ),
            )


# ============================================================
# TAB 4
# QUALITY & RISK
# ============================================================

with tab_quality:

    qdf = (
        filtered.copy()
    )


    section_header(
        "Quality & Risk Intelligence",
        (
            "Where rejections, backlog and "
            "field-performance risks are concentrated"
        ),
    )


    c1, c2 = st.columns(
        [
            1.2,
            1,
        ]
    )


    with c1:

        quality_reasons = (
            rejection_summary(
                qdf,
                top_n=15,
            )
        )


        render_chart(
            fig_rejection_pareto(
                quality_reasons,
                title=(
                    "Rejection Pareto "
                    "| Current Filter"
                ),
            ),
            key=(
                "quality_"
                "rejection_pareto"
            ),
        )


    with c2:

        quality_staff = (
            staff_summary(
                qdf,
                top_n=35,
            )
        )


        render_chart(
            fig_staff_scatter(
                quality_staff
            ),
            key=(
                "quality_"
                "staff_performance"
            ),
        )


    c1, c2 = st.columns(
        2
    )


    with c1:

        quality_components = (
            quality_summary(
                qdf
            )
        )


        render_chart(
            fig_quality_components(
                quality_components,
                title=(
                    "QA Component "
                    "Profile"
                ),
            ),
            key=(
                "quality_"
                "component_profile"
            ),
        )


    with c2:

        quality_qc = (
            qc_reviewer_summary(
                qdf
            )
        )


        render_chart(
            fig_qc_reviewer(
                quality_qc
            ),
            key=(
                "quality_"
                "qa_reviewer"
            ),
        )


# ============================================================
# TAB 5
# GEOGRAPHY
# ============================================================

with tab_geo:

    section_header(
        "Geographic Intelligence",
        (
            "Province and district performance "
            "with quality-risk context"
        ),
    )


    geo_df = (
        filtered.copy()
    )


    province_data = (
        province_summary(
            geo_df
        )
        .head(
            25
        )
    )


    province_quality = (
        province_quality_index(
            geo_df
        )
        .head(
            25
        )
    )


    c1, c2 = st.columns(
        [
            1.15,
            1,
        ]
    )


    with c1:

        render_chart(
            fig_province_status(
                province_data,
                title=(
                    "Province "
                    "Status Mix"
                ),
            ),
            key=(
                "geography_"
                "province_status"
            ),
        )


    with c2:

        render_chart(
            fig_province_quality_scatter(
                province_quality
            ),
            key=(
                "geography_"
                "province_quality"
            ),
        )


    district_data = (
        district_summary(
            geo_df
        )
        .head(
            25
        )
    )


    render_chart(
        fig_category_bar(
            district_data,
            "District",
            "Records",
            (
                "Top Districts "
                "by Volume"
            ),
        ),
        key=(
            "geography_"
            "district_volume"
        ),
    )


# ============================================================
# TAB 6
# TIME INTELLIGENCE
# ============================================================

with tab_time:

    section_header(
        "Time Intelligence",
        (
            "Monthly flow, daily intensity "
            "and calendar-based operational patterns"
        ),
    )


    time_df = (
        filtered[
            filtered[
                "date"
            ].notna()
        ]
        .copy()
    )


    time_monthly = (
        monthly_summary(
            time_df,
            selected_year,
        )
    )


    c1, c2 = st.columns(
        [
            1.2,
            1,
        ]
    )


    with c1:

        render_chart(
            fig_monthly_trend(
                time_monthly,
                title=(
                    "Monthly Collection "
                    "& QA Trend"
                ),
            ),
            key=(
                "time_"
                "monthly_trend"
            ),
        )


    with c2:

        calendar_data = (
            calendar_heatmap_data(
                time_df,
                selected_year,
            )
        )


        render_chart(
            fig_calendar_heatmap(
                calendar_data
            ),
            key=(
                "time_"
                "calendar_heatmap"
            ),
        )


# ============================================================
# TAB 7
# DATA EXPLORER
# ============================================================

with tab_explorer:

    section_header(
        "Public Data Explorer",
        (
            "Privacy-safe operational records. "
            "Beneficiary names and phone numbers "
            "are intentionally excluded."
        ),
    )


    safe_columns = [
        "project",
        "subsource",
        "date",
        "tool_type",
        "province",
        "district",
        "status",
        "rejection_reason",
        "phase",
        "discipline",
        "gender",
    ]


    safe_columns = [
        column
        for column
        in safe_columns
        if column
        in filtered.columns
    ]


    public_view = (
        filtered[
            safe_columns
        ]
        .copy()
    )


    st.caption(
        (
            "Records in current filtered view: "
            f"{len(public_view):,}"
        )
    )


    st.dataframe(
        public_view.sort_values(
            "date",
            ascending=False,
            na_position="last",
        ),
        use_container_width=True,
        hide_index=True,
        height=590,
    )


    csv_data = (
        public_view
        .to_csv(
            index=False
        )
        .encode(
            "utf-8-sig"
        )
    )


    st.download_button(
        (
            "Download filtered "
            "public CSV"
        ),
        data=csv_data,
        file_name=(
            "UNICEF_public_dashboard_"
            f"{selected_year}.csv"
        ),
        mime="text/csv",
        use_container_width=True,
        key=(
            "explorer_"
            "download_csv"
        ),
    )


# ============================================================
# FOOTER
# ============================================================

footer(
    source=(
        "Google Sheet → "
        "internal project tabs only"
    ),
    spreadsheet_id=(
        source_meta[
            "spreadsheet_id"
        ]
    ),
)

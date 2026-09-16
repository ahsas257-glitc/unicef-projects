from __future__ import annotations

import io
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from src.config import APP_TITLE, APP_SUBTITLE, PROJECTS, SCOPES, DEFAULT_YEAR
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
)
from src.ui import (
    inject_css,
    hero,
    metric_card,
    section_header,
    insight_card,
    pill,
    footer,
    show_empty_state,
)

st.set_page_config(
    page_title="UNICEF Portfolio Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# -----------------------------
# Header
# -----------------------------
hero(
    title=APP_TITLE,
    subtitle=APP_SUBTITLE,
    badge="LIVE GOOGLE SHEETS",
)

# -----------------------------
# Sidebar / data source
# -----------------------------
with st.sidebar:
    st.markdown("### CONTROL CENTER")
    st.caption("All calculations use the internal project tabs in the connected Google Sheet.")

    if st.button("↻ Refresh live data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

try:
    sheet_frames, source_meta = load_google_sheet()
except Exception as exc:
    st.error("The dashboard could not connect to Google Sheets.")
    st.code(str(exc))
    st.info(
        "Add the service-account credentials in Streamlit Cloud → App → Settings → Secrets, "
        "then share the Google Sheet with the service-account email as Viewer."
    )
    st.stop()

master, model_meta = build_master_dataset(sheet_frames)

if master.empty:
    show_empty_state(
        "No usable records were found in the connected project sheets.",
        "Check the sheet names and headers in the Google Sheet.",
    )
    st.stop()

# -----------------------------
# Global filters
# -----------------------------
years = sorted(int(x) for x in master["year"].dropna().unique())
if not years:
    years = [DEFAULT_YEAR]

default_year = DEFAULT_YEAR if DEFAULT_YEAR in years else max(years)

query_project = None
try:
    query_project = st.query_params.get("project")
except Exception:
    pass

project_options = ["All Projects"] + PROJECTS
default_project_idx = 0
if query_project in PROJECTS:
    default_project_idx = project_options.index(query_project)

with st.sidebar:
    st.markdown("#### GLOBAL FILTERS")
    selected_year = st.selectbox(
        "Reporting year",
        years,
        index=years.index(default_year),
    )

    selected_project = st.selectbox(
        "Project view",
        project_options,
        index=default_project_idx,
    )

    try:
        if selected_project == "All Projects":
            st.query_params.pop("project", None)
        else:
            st.query_params["project"] = selected_project
    except Exception:
        pass

    include_undated_vt = st.toggle(
        "Include undated VT KII/FGD in totals",
        value=True,
        help="These records stay in VT totals but cannot appear in time-trend charts until they have a date.",
    )

# Base year filter first, while optionally retaining undated VT KII/FGD
year_mask = master["year"].eq(selected_year)
if include_undated_vt:
    year_mask |= (
        master["date"].isna()
        & master["project"].eq("VT")
        & master["subsource"].eq("VT KII/FGD")
    )
year_df = master.loc[year_mask].copy()

project_df = year_df.copy()
if selected_project != "All Projects":
    project_df = project_df[project_df["project"].eq(selected_project)].copy()

with st.sidebar:
    province_values = sorted(
        x for x in project_df["province"].fillna("").astype(str).unique()
        if x.strip() and x != "Unknown"
    )
    selected_provinces = st.multiselect("Province", province_values, default=[])

    status_values = ["Approved", "Rejected", "Pending", "Unreviewed"]
    selected_statuses = st.multiselect(
        "QA status",
        status_values,
        default=status_values,
    )

    tool_values = sorted(
        x for x in project_df["tool_type"].fillna("").astype(str).unique()
        if x.strip() and x != "Unknown"
    )
    selected_tools = st.multiselect("Tool / instrument", tool_values, default=[])

    search_text = st.text_input(
        "Search aggregate fields",
        placeholder="Province, district, tool, rejection reason...",
    )

filtered = apply_filters(
    project_df,
    provinces=selected_provinces,
    statuses=selected_statuses,
    tools=selected_tools,
    search_text=search_text,
)

# -----------------------------
# Context strip
# -----------------------------
latest_dated = year_df["date"].dropna().max()
latest_date_text = latest_dated.strftime("%d %b %Y") if pd.notna(latest_dated) else "No dated records"
refresh_text = datetime.now(ZoneInfo("Asia/Kabul")).strftime("%d %b %Y • %H:%M")

st.markdown(
    f"""
    <div class="context-strip">
      <span>{pill(f"Year {selected_year}")}</span>
      <span>{pill(selected_project)}</span>
      <span>{pill(f"Latest data: {latest_date_text}")}</span>
      <span>{pill(f"Rows in current view: {len(filtered):,}")}</span>
      <span>{pill(f"Refreshed: {refresh_text}")}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Main navigation
# -----------------------------
tab_overview, tab_project, tab_quality, tab_geo, tab_explorer = st.tabs(
    [
        "Executive Overview",
        "Project Deep Dive",
        "Quality Intelligence",
        "Geography & Trends",
        "Data Explorer",
    ]
)

# -----------------------------
# Executive Overview
# -----------------------------
with tab_overview:
    summary = portfolio_summary(year_df, SCOPES, projects=(PROJECTS if selected_project == "All Projects" else [selected_project]))

    total_scope = int(summary["Scope"].sum())
    total_received = int(summary["Received"].sum())
    total_approved = int(summary["Approved"].sum())
    total_rejected = int(summary["Rejected"].sum())
    total_pending = int(summary["Pending / Unreviewed"].sum())
    total_remaining = int(summary["Remaining"].sum())
    progress = total_approved / total_scope if total_scope else 0
    approval_rate = total_approved / total_received if total_received else 0
    reviewed_rate = (total_approved + total_rejected) / total_received if total_received else 0

    section_header("Executive Snapshot", "Live portfolio metrics computed from project tabs")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        metric_card("Scope", f"{total_scope:,}", "Configured 2026 target", "neutral")
    with c2:
        metric_card("Received", f"{total_received:,}", f"{total_received / total_scope:.1%} of scope" if total_scope else "—", "blue")
    with c3:
        metric_card("Approved", f"{total_approved:,}", f"{approval_rate:.1%} approval rate", "green")
    with c4:
        metric_card("Rejected", f"{total_rejected:,}", f"{total_rejected / total_received:.1%} of received" if total_received else "—", "red")
    with c5:
        metric_card("Pending QA", f"{total_pending:,}", f"{total_pending / total_received:.1%} backlog" if total_received else "—", "amber")
    with c6:
        metric_card("Completion", f"{progress:.1%}", f"{total_remaining:,} remaining", "purple")

    c1, c2, c3 = st.columns([1.1, 1.1, 0.9])
    with c1:
        st.plotly_chart(fig_scope_completion(summary), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(fig_status_mix(total_approved, total_rejected, total_pending), use_container_width=True, config={"displayModeBar": False})
    with c3:
        dq = data_quality_summary(year_df, selected_year)
        metric_card("QC Reviewed", f"{reviewed_rate:.1%}", "Approved + Rejected / Received", "cyan")
        metric_card("Undated VT KII/FGD", f"{dq['undated_vt_kii_fgd']:,}", "Included in totals, excluded from trends", "amber")
        metric_card("Future-dated", f"{dq['future_dated']:,}", "Check date quality", "red" if dq["future_dated"] else "green")
        metric_card("Missing rejection reason", f"{dq['rejected_missing_reason']:,}", "Rejected records without documented reason", "red" if dq["rejected_missing_reason"] else "green")

    section_header("Management Intelligence", "Automatic rule-based interpretation of the live data")
    insights = executive_insights(summary, year_df, selected_year)
    cols = st.columns(min(3, max(1, len(insights))))
    for idx, item in enumerate(insights):
        with cols[idx % len(cols)]:
            insight_card(item["title"], item["text"], item["level"])

    section_header("Portfolio Health Matrix", "Completion, approval, rejection, QC review and backlog by project")
    st.plotly_chart(fig_project_health_matrix(summary), use_container_width=True, config={"displayModeBar": False})

    section_header("Project Performance Table", "A decision-ready view of scope, quality and backlog")
    display_summary = summary.copy()
    percent_cols = [
        "Completion %",
        "Collection Coverage %",
        "Approval Rate %",
        "Rejection Rate %",
        "QC Reviewed %",
        "Backlog %",
    ]
    st.dataframe(
        display_summary.style.format({
            "Scope": "{:,.0f}",
            "Received": "{:,.0f}",
            "Approved": "{:,.0f}",
            "Rejected": "{:,.0f}",
            "Pending / Unreviewed": "{:,.0f}",
            "Remaining": "{:,.0f}",
            **{c: "{:.1%}" for c in percent_cols},
        }),
        use_container_width=True,
        hide_index=True,
        height=310,
    )

# -----------------------------
# Project Deep Dive
# -----------------------------
with tab_project:
    active_project = selected_project
    if active_project == "All Projects":
        active_project = st.selectbox("Choose a project for the deep dive", PROJECTS, key="deep_dive_project")

    deep_df = year_df[year_df["project"].eq(active_project)].copy()
    psummary = project_summary(deep_df, active_project, SCOPES.get(active_project, 0))

    section_header(
        f"{active_project} Deep Dive",
        "A dedicated project dashboard with context-specific visualizations",
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        metric_card("Received", f"{psummary['Received']:,}", f"{psummary['Collection Coverage %']:.1%} of scope", "blue")
    with k2:
        metric_card("Approved", f"{psummary['Approved']:,}", f"{psummary['Approval Rate %']:.1%} approval", "green")
    with k3:
        metric_card("Rejected", f"{psummary['Rejected']:,}", f"{psummary['Rejection Rate %']:.1%} rejected", "red")
    with k4:
        metric_card("Pending", f"{psummary['Pending / Unreviewed']:,}", f"{psummary['Backlog %']:.1%} backlog", "amber")
    with k5:
        metric_card("Remaining", f"{psummary['Remaining']:,}", f"{psummary['Completion %']:.1%} complete", "purple")
    with k6:
        metric_card("Health", psummary["Health Flag"], psummary["Priority Action"], "cyan")

    if deep_df.empty:
        show_empty_state("No records in this project for the selected year.", "Change the year or project filter.")
    else:
        monthly = monthly_summary(deep_df, selected_year)

        r1c1, r1c2 = st.columns([1.35, 1])
        with r1c1:
            st.plotly_chart(fig_monthly_trend(monthly, title=f"{active_project} Monthly Trend"), use_container_width=True, config={"displayModeBar": False})
        with r1c2:
            project_breakdowns = project_specific_breakdowns(deep_df, active_project)
            if active_project == "Moraa" and project_breakdowns.get("sunburst") is not None:
                st.plotly_chart(
                    fig_sunburst(project_breakdowns["sunburst"], "Phase", "Discipline", "Status"),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            elif active_project == "VT":
                vt_tools = vt_tool_summary(deep_df)
                st.plotly_chart(fig_vt_tool_bubble(vt_tools), use_container_width=True, config={"displayModeBar": False})
            else:
                q = quality_summary(deep_df)
                st.plotly_chart(fig_quality_components(q, title="QA Component Profile"), use_container_width=True, config={"displayModeBar": False})

        r2c1, r2c2 = st.columns([1, 1])
        with r2c1:
            provinces = province_summary(deep_df).head(15)
            st.plotly_chart(fig_province_status(provinces, title=f"{active_project} by Province"), use_container_width=True, config={"displayModeBar": False})
        with r2c2:
            reasons = rejection_summary(deep_df, top_n=12)
            st.plotly_chart(fig_rejection_pareto(reasons, title=f"{active_project} Rejection Pareto"), use_container_width=True, config={"displayModeBar": False})

        section_header("Project-Specific Intelligence", "Visuals change based on the data structure of the selected project")
        project_breakdowns = project_specific_breakdowns(deep_df, active_project)

        if active_project == "VT":
            vt_summary = vt_tool_summary(deep_df)
            st.dataframe(
                vt_summary.style.format({
                    "Approval Rate %": "{:.1%}",
                    "Rejection Rate %": "{:.1%}",
                    "QC Reviewed %": "{:.1%}",
                    "Backlog %": "{:.1%}",
                }),
                use_container_width=True,
                hide_index=True,
            )

        elif active_project == "Moraa":
            a, b, c = st.columns(3)
            with a:
                st.plotly_chart(fig_category_bar(project_breakdowns.get("phase"), "Phase", "Records", "Phase"), use_container_width=True, config={"displayModeBar": False})
            with b:
                st.plotly_chart(fig_category_bar(project_breakdowns.get("discipline"), "Discipline", "Records", "Discipline"), use_container_width=True, config={"displayModeBar": False})
            with c:
                st.plotly_chart(fig_category_bar(project_breakdowns.get("gender"), "Gender", "Records", "Gender"), use_container_width=True, config={"displayModeBar": False})

        else:
            a, b = st.columns(2)
            with a:
                st.plotly_chart(
                    fig_category_bar(project_breakdowns.get("tool"), "Tool", "Records", "Tool / Instrument"),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            with b:
                st.plotly_chart(
                    fig_category_bar(project_breakdowns.get("qc_reviewer"), "QC Reviewer", "Records", "QA Reviewer"),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

# -----------------------------
# Quality Intelligence
# -----------------------------
with tab_quality:
    qdf = filtered.copy()
    section_header("Quality Intelligence", "Rejections, QA backlog, field-staff performance and data-quality signals")

    left, right = st.columns([1.25, 1])
    with left:
        reasons = rejection_summary(qdf, top_n=15)
        st.plotly_chart(fig_rejection_pareto(reasons, title="Rejection Pareto | Current Filter"), use_container_width=True, config={"displayModeBar": False})
    with right:
        staff = staff_summary(qdf, top_n=30)
        st.plotly_chart(fig_staff_scatter(staff), use_container_width=True, config={"displayModeBar": False})

    section_header("Quality Metrics by Project", "QA outcome rates calculated from the selected live records")
    quality_table = portfolio_summary(
        qdf,
        SCOPES,
        projects=(PROJECTS if selected_project == "All Projects" else [selected_project]),
        honor_input_as_filtered=True,
    )
    st.dataframe(
        quality_table.style.format({
            "Completion %": "{:.1%}",
            "Collection Coverage %": "{:.1%}",
            "Approval Rate %": "{:.1%}",
            "Rejection Rate %": "{:.1%}",
            "QC Reviewed %": "{:.1%}",
            "Backlog %": "{:.1%}",
        }),
        use_container_width=True,
        hide_index=True,
    )

# -----------------------------
# Geography & Trends
# -----------------------------
with tab_geo:
    section_header("Geography & Trends", "Where the portfolio is active, and how delivery and QA change over time")

    geo_df = filtered.copy()
    prov = province_summary(geo_df).head(20)
    monthly = monthly_summary(geo_df[geo_df["date"].notna()], selected_year)

    g1, g2 = st.columns([1.15, 1])
    with g1:
        st.plotly_chart(fig_province_status(prov, title="Province Status Mix"), use_container_width=True, config={"displayModeBar": False})
    with g2:
        st.plotly_chart(fig_monthly_trend(monthly, title="Monthly Collection & QA Trend"), use_container_width=True, config={"displayModeBar": False})

    section_header("Province Performance Table", "Volume, approval, rejection and pending QA")
    st.dataframe(
        prov.style.format({
            "Approval Rate %": "{:.1%}",
            "Rejection Rate %": "{:.1%}",
            "Backlog %": "{:.1%}",
        }),
        use_container_width=True,
        hide_index=True,
        height=520,
    )

# -----------------------------
# Data Explorer
# -----------------------------
with tab_explorer:
    section_header("Public Data Explorer", "A privacy-safe record view. Personal names and phone numbers are intentionally excluded.")

    safe_cols = [
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
    safe_cols = [c for c in safe_cols if c in filtered.columns]
    public_view = filtered[safe_cols].copy()

    st.caption(f"Records in current filtered view: {len(public_view):,}")
    st.dataframe(
        public_view.sort_values("date", ascending=False, na_position="last"),
        use_container_width=True,
        hide_index=True,
        height=560,
    )

    csv = public_view.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Download filtered public CSV",
        data=csv,
        file_name=f"UNICEF_public_dashboard_{selected_year}.csv",
        mime="text/csv",
        use_container_width=True,
    )

footer(
    source="Google Sheet → internal project tabs only",
    spreadsheet_id=source_meta["spreadsheet_id"],
)

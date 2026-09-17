from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BG = "rgba(0,0,0,0)"
TEXT = "#DCE7F7"
MUTED = "#94A3B8"
GRID = "rgba(148,163,184,.12)"
BLUE = "#2F7CF6"
CYAN = "#22D3EE"
GREEN = "#22C55E"
RED = "#EF4444"
AMBER = "#F59E0B"
PURPLE = "#8B5CF6"
SLATE = "#475569"

def _layout(fig, height=380, margin=None):
    fig.update_layout(
        height=height,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=12),
        margin=margin or dict(l=15, r=15, t=55, b=15),
def _layout(
    fig,
    height=390,
    margin=None,
):
    """
    Apply the global visual style to every Plotly chart.

    The top margin and legend position are intentionally spacious
    so chart titles and legends never collide.
    """

    fig.update_layout(

        height=height,

        paper_bgcolor=BG,

        plot_bgcolor=BG,

        font=dict(
            family="Inter, Segoe UI, sans-serif",
            color=TEXT,
            size=12,
        ),

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title=dict(
            x=0.02,
            y=0.97,

            xanchor="left",
            yanchor="top",

            font=dict(
                size=17,
                color="#F8FBFF",
            ),

            pad=dict(
                t=4,
                b=14,
            ),
        ),

        # ----------------------------------------------------
        # MARGINS
        # ----------------------------------------------------

        margin=(
            margin
            or dict(
                l=20,
                r=20,
                t=95,
                b=22,
            )
        ),

        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        legend=dict(

            orientation="h",

            # Put legend below the title instead of beside it.
            yanchor="bottom",

            y=1.01,

            xanchor="left",

            x=0.02,

            font=dict(
                color=MUTED,
                size=11,
            ),

            bgcolor="rgba(0,0,0,0)",

            borderwidth=0,

            itemclick="toggle",

            itemdoubleclick="toggleothers",
        ),

        # ----------------------------------------------------
        # HOVER
        # ----------------------------------------------------

        hoverlabel=dict(
            bgcolor="#0B192B",
            font_color="white",
            bordercolor="#1E334D",
        ),
    )


    fig.update_xaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,

        tickfont=dict(
            color=MUTED,
        ),

        title_font=dict(
            color=MUTED,
        ),
    )


    fig.update_yaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,

        tickfont=dict(
            color=MUTED,
        ),

        title_font=dict(
            color=MUTED,
        ),
    )


    return fig
        ),
        hoverlabel=dict(bgcolor="#0F172A", font_color="white"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color=MUTED), title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, tickfont=dict(color=MUTED), title_font=dict(color=MUTED))
    return fig

def fig_scope_completion(summary):
    if summary.empty:
        return _layout(go.Figure(), 360)

    work = summary.copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=work["Project"],
        x=work["Approved"],
        name="Approved",
        orientation="h",
        marker_color=GREEN,
        hovertemplate="<b>%{y}</b><br>Approved: %{x:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=work["Project"],
        x=work["Remaining"],
        name="Remaining",
        orientation="h",
        marker_color="#334155",
        hovertemplate="<b>%{y}</b><br>Remaining: %{x:,}<extra></extra>",
    ))
    fig.update_layout(
        barmode="stack",
        title="Completion vs Remaining Scope",
        xaxis_title="Records",
        yaxis_title="",
    )
    return _layout(fig, 390)

def fig_status_mix(approved, rejected, pending):
    labels = ["Approved", "Rejected", "Pending"]
    values = [approved, rejected, pending]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=.72,
        sort=False,
        marker_colors=[GREEN, RED, AMBER],
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value:,} records<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        title="Portfolio QA Status",
        annotations=[dict(
            text=f"<b>{sum(values):,}</b><br><span style='font-size:11px'>received</span>",
            x=.5, y=.5, showarrow=False, font=dict(color=TEXT, size=20)
        )],
        showlegend=True,
    )
    return _layout(fig, 390)

def fig_monthly_trend(monthly, title="Monthly Collection & QA Trend"):
    fig = go.Figure()
    colors = {
        "Received": BLUE,
        "Approved": GREEN,
        "Rejected": RED,
        "Pending": AMBER,
    }
    for col in ["Received", "Approved", "Rejected", "Pending"]:
        if col in monthly.columns:
            fig.add_trace(go.Scatter(
                x=monthly["Month"],
                y=monthly[col],
                mode="lines+markers",
                name=col,
                line=dict(width=3, color=colors[col]),
                marker=dict(size=7),
                hovertemplate=f"<b>%{{x|%b %Y}}</b><br>{col}: %{{y:,}}<extra></extra>",
            ))
    fig.update_layout(title=title, xaxis_title="", yaxis_title="Records")
    return _layout(fig, 390)

def fig_project_health_matrix(summary):
    if summary.empty:
        return _layout(go.Figure(), 420)

    metrics = [
        "Completion %",
        "Approval Rate %",
        "QC Reviewed %",
        "Rejection Rate %",
        "Backlog %",
    ]
    z = summary[metrics].to_numpy(dtype=float)
    # Risk-adjust the last two so higher values visually mean worse health.
    display = z.copy()
    display[:, 3] = 1 - display[:, 3]
    display[:, 4] = 1 - display[:, 4]

    text = [[f"{v:.1%}" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=display,
        x=["Completion", "Approval", "QC Reviewed", "Low Rejection", "Low Backlog"],
        y=summary["Project"],
        text=text,
        texttemplate="%{text}",
        colorscale=[
            [0, "#7F1D1D"],
            [.45, "#F59E0B"],
            [1, "#16A34A"],
        ],
        zmin=0,
        zmax=1,
        colorbar=dict(title="Health", tickvals=[0, .5, 1], ticktext=["Weak", "Watch", "Strong"]),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
    ))
    fig.update_layout(title="Portfolio Health Matrix", xaxis_title="", yaxis_title="")
    return _layout(fig, 420)

def fig_province_status(prov, title="Province Status Mix"):
    if prov is None or prov.empty:
        return _layout(go.Figure(), 420)

    work = prov.sort_values("Received", ascending=True).tail(18)
    fig = go.Figure()
    for col, color in [("Approved", GREEN), ("Rejected", RED), ("Pending", AMBER)]:
        fig.add_trace(go.Bar(
            y=work["Province"],
            x=work[col],
            name=col,
            orientation="h",
            marker_color=color,
            hovertemplate=f"<b>%{{y}}</b><br>{col}: %{{x:,}}<extra></extra>",
        ))
    fig.update_layout(barmode="stack", title=title, xaxis_title="Records", yaxis_title="")
    return _layout(fig, 480)

def fig_rejection_pareto(reasons, title="Top Rejection Reasons"):
    if reasons is None or reasons.empty:
        fig = go.Figure()
        fig.add_annotation(text="No rejected records in the current view", showarrow=False, font=dict(color=MUTED))
        fig.update_layout(title=title)
        return _layout(fig, 430)

    work = reasons.sort_values("Count", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=work["Reason"],
        x=work["Count"],
        orientation="h",
        marker=dict(
            color=work["Count"],
            colorscale=[[0, "#7C3AED"], [1, RED]],
        ),
        name="Rejected",
        hovertemplate="<b>%{y}</b><br>Rejected: %{x:,}<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title="Rejected records", yaxis_title="")
    fig.update_yaxes(automargin=True)
    return _layout(fig, 500, margin=dict(l=20, r=10, t=55, b=15))

def fig_vt_tool_bubble(vt):
    if vt is None or vt.empty:
        return _layout(go.Figure(), 430)

    work = vt.copy()
    work["Bubble"] = np.maximum(work["Received"], 10)
    fig = px.scatter(
        work,
        x="Approval Rate %",
        y="Rejection Rate %",
        size="Bubble",
        color="Backlog %",
        hover_name="VT Tool Type",
        hover_data={
            "Received": True,
            "Approved": True,
            "Rejected": True,
            "Pending": True,
            "Bubble": False,
        },
        color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
        size_max=50,
    )
    fig.update_layout(
        title="VT Tool Risk Map",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        coloraxis_colorbar=dict(title="Backlog"),
    )
    return _layout(fig, 430)

def fig_staff_scatter(staff):
    if staff is None or staff.empty:
        return _layout(go.Figure(), 480)

    fig = px.scatter(
        staff,
        x="Received",
        y="Approval Rate %",
        size="Received",
        color="Rejection Rate %",
        hover_name="Field Staff",
        hover_data=["Approved", "Rejected", "Pending"],
        color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"],
        size_max=38,
    )
    fig.update_layout(
        title="Field Staff Performance Map (Pseudonymized)",
        yaxis_tickformat=".0%",
        coloraxis_colorbar=dict(title="Rejection"),
    )
    return _layout(fig, 480)

def fig_category_bar(data, category, value, title):
    if data is None or data.empty:
        return _layout(go.Figure(), 380)

    work = data.sort_values(value, ascending=True).tail(15)
    fig = go.Figure(go.Bar(
        y=work[category],
        x=work[value],
        orientation="h",
        marker_color=BLUE,
        hovertemplate="<b>%{y}</b><br>Records: %{x:,}<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title="Records", yaxis_title="")
    return _layout(fig, 400)

def fig_sunburst(data, level1, level2, level3):
    if data is None or data.empty:
        return _layout(go.Figure(), 420)
    work = data.copy()
    work = work.replace("", "Unknown").fillna("Unknown")
    fig = px.sunburst(
        work,
        path=[level1, level2, level3],
        color=level3,
        color_discrete_map={
            "Approved": GREEN,
            "Rejected": RED,
            "Pending": AMBER,
            "Unreviewed": SLATE,
        },
    )
    fig.update_layout(title="Moraa Phase → Discipline → QA Status")
    return _layout(fig, 440)

def fig_quality_components(q, title="QA Component Profile"):
    if q is None or q.empty:
        fig = go.Figure()
        fig.add_annotation(text="No numeric component scores are available in this project view", showarrow=False, font=dict(color=MUTED))
        fig.update_layout(title=title)
        return _layout(fig, 420)

    fig = go.Figure(go.Bar(
        x=q["Metric"],
        y=q["Average"],
        marker_color=[BLUE, PURPLE, CYAN, GREEN, AMBER][:len(q)],
        text=[f"{v:.2f}" for v in q["Average"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Average: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(title=title, xaxis_title="", yaxis_title="Average score")
    return _layout(fig, 420)


def fig_speedometer(value, title="Portfolio Completion"):
    value = max(0.0, min(float(value), 1.0))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        number={"suffix": "%", "font": {"size": 38, "color": TEXT}},
        title={"text": title, "font": {"size": 18, "color": TEXT}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": MUTED},
            "bar": {"color": BLUE, "thickness": .24},
            "bgcolor": "#0A1728",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25], "color": "#341B28"},
                {"range": [25, 50], "color": "#3A2B18"},
                {"range": [50, 75], "color": "#19344A"},
                {"range": [75, 100], "color": "#173427"},
            ],
            "threshold": {"line": {"color": CYAN, "width": 3}, "thickness": .75, "value": value * 100},
        },
    ))
    return _layout(fig, 390)


def fig_project_radar(summary):
    if summary.empty:
        return _layout(go.Figure(), 430)
    theta = ["Completion", "Approval", "QC Reviewed", "Low Rejection", "Low Backlog"]
    colors = [BLUE, GREEN, CYAN, PURPLE, AMBER, "#14B8A6"]
    fig = go.Figure()
    for i, row in summary.reset_index(drop=True).iterrows():
        vals = [
            row["Completion %"], row["Approval Rate %"], row["QC Reviewed %"],
            1 - row["Rejection Rate %"], 1 - row["Backlog %"],
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=theta + [theta[0]], fill="toself",
            opacity=.18, name=row["Project"], line=dict(width=2, color=colors[i % len(colors)])
        ))
    fig.update_layout(
        title="Project Performance Radar",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 1], tickformat=".0%", gridcolor=GRID, color=MUTED),
            angularaxis=dict(gridcolor=GRID, color=MUTED),
        ),
    )
    return _layout(fig, 440)


def fig_treemap(summary):
    if summary.empty:
        return _layout(go.Figure(), 430)
    fig = px.treemap(
        summary, path=["Project"], values="Scope", color="Completion %",
        color_continuous_scale=["#7F1D1D", "#D97706", "#15803D"],
        hover_data=["Received", "Approved", "Rejected", "Pending / Unreviewed"],
    )
    fig.update_layout(title="Portfolio Scope & Completion Treemap", coloraxis_colorbar=dict(title="Completion"))
    return _layout(fig, 450)


def fig_funnel(summary):
    if summary.empty:
        return _layout(go.Figure(), 430)
    scope = summary["Scope"].sum()
    received = summary["Received"].sum()
    reviewed = summary["Approved"].sum() + summary["Rejected"].sum()
    approved = summary["Approved"].sum()
    fig = go.Figure(go.Funnel(
        y=["Scope", "Received", "QC Reviewed", "Approved"],
        x=[scope, received, reviewed, approved],
        textinfo="value+percent initial",
        marker={"color": [SLATE, BLUE, CYAN, GREEN]},
    ))
    fig.update_layout(title="Portfolio Delivery Funnel")
    return _layout(fig, 430)


def fig_waterfall(summary):
    if summary.empty:
        return _layout(go.Figure(), 430)
    fig = go.Figure(go.Bar(
        x=summary["Project"], y=summary["Remaining"],
        marker=dict(color=summary["Remaining"], colorscale=[[0, "#164E63"], [1, PURPLE]]),
        text=summary["Remaining"], textposition="outside",
    ))
    fig.update_layout(title="Remaining Scope Pressure", yaxis_title="Remaining approvals", xaxis_title="")
    return _layout(fig, 430)


def fig_province_quality_scatter(pqi):
    if pqi is None or pqi.empty:
        return _layout(go.Figure(), 470)
    fig = px.scatter(
        pqi, x="Received", y="Quality Index", size="Received", color="Rejection Rate %",
        hover_name="Province", hover_data=["Approved", "Rejected", "Pending", "Approval Rate %", "Backlog %"],
        color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"], size_max=45,
    )
    fig.update_layout(title="Province Quality vs Volume", yaxis_tickformat=".0%", coloraxis_colorbar=dict(title="Rejection"))
    return _layout(fig, 470)


def fig_qc_reviewer(qc):
    if qc is None or qc.empty:
        return _layout(go.Figure(), 430)
    work = qc.sort_values("Reviewed", ascending=True).tail(15)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=work["QA Reviewer"], x=work["Approved"], name="Approved", orientation="h", marker_color=GREEN))
    fig.add_trace(go.Bar(y=work["QA Reviewer"], x=work["Rejected"], name="Rejected", orientation="h", marker_color=RED))
    fig.update_layout(barmode="stack", title="QA Reviewer Workload & Outcomes", xaxis_title="Reviewed records", yaxis_title="")
    return _layout(fig, 460)


def fig_calendar_heatmap(cal):
    if cal is None or cal.empty:
        return _layout(go.Figure(), 430)
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot = cal.pivot_table(index="Weekday", columns="Month", values="Records", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(index=weekdays, columns=months, fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale=[[0, "#0B192B"], [.35, "#1D4ED8"], [1, "#22D3EE"]],
        colorbar=dict(title="Records"), text=pivot.values, texttemplate="%{text}",
    ))
    fig.update_layout(title="Collection Intensity Heatmap")
    return _layout(fig, 430)

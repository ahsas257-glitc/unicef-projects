from __future__ import annotations

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# GLOBAL DESIGN TOKENS
# ============================================================

BG = "rgba(0,0,0,0)"

TEXT = "#E8F0FB"
TEXT_BRIGHT = "#F8FBFF"
MUTED = "#90A2B9"

GRID = "rgba(148,163,184,0.10)"

BLUE = "#3B82F6"
CYAN = "#22D3EE"
GREEN = "#22C55E"
RED = "#EF4444"
AMBER = "#F59E0B"
PURPLE = "#8B5CF6"
SLATE = "#475569"

NAVY = "#0B192B"
NAVY_LIGHT = "#10223A"


# ============================================================
# GLOBAL CHART LAYOUT
# ============================================================

def _layout(
    fig,
    height: int = 420,
    margin: dict | None = None,
    *,
    showlegend: bool | None = None,
    legend_y: float = 1.015,
):
    """
    Apply the global dashboard visual system.

    Major design goals:
    - Keep chart title clearly separated from legend.
    - Provide enough top breathing room.
    - Maintain a premium dark dashboard appearance.
    - Standardize axes, hover cards and typography.
    """

    # --------------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------------

    layout_updates = dict(

        height=height,

        paper_bgcolor=BG,

        plot_bgcolor=BG,

        font=dict(
            family=(
                "Inter, "
                "Segoe UI, "
                "Arial, "
                "sans-serif"
            ),
            color=TEXT,
            size=12,
        ),

        # ----------------------------------------------------
        # CHART TITLE
        # ----------------------------------------------------

        title=dict(

            x=0.02,

            # Keep title at the very top of the card.
            y=0.985,

            xanchor="left",
            yanchor="top",

            font=dict(
                size=17,
                color=TEXT_BRIGHT,
                family=(
                    "Inter, "
                    "Segoe UI, "
                    "Arial, "
                    "sans-serif"
                ),
            ),

            pad=dict(
                t=2,
                b=20,
            ),
        ),

        # ----------------------------------------------------
        # MARGINS
        # ----------------------------------------------------

        margin=(
            margin
            if margin is not None
            else dict(
                l=24,
                r=24,

                # IMPORTANT:
                # Larger top margin creates a dedicated zone
                # for both title and legend.
                t=115,

                b=28,
            )
        ),

        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        legend=dict(

            # Horizontal legend looks cleaner in dashboard cards.
            orientation="h",

            # Legend is located under the title
            # and above the actual plot area.
            yanchor="bottom",

            y=legend_y,

            xanchor="left",

            x=0.02,

            font=dict(
                color=MUTED,
                size=11,
            ),

            bgcolor="rgba(0,0,0,0)",

            bordercolor="rgba(0,0,0,0)",

            borderwidth=0,

            itemclick="toggle",

            itemdoubleclick="toggleothers",

            tracegroupgap=8,
        ),

        # ----------------------------------------------------
        # HOVER TOOLTIP
        # ----------------------------------------------------

        hoverlabel=dict(
            bgcolor=NAVY,
            bordercolor="#1E334D",

            font=dict(
                color="#FFFFFF",
                size=12,
                family=(
                    "Inter, "
                    "Segoe UI, "
                    "Arial, "
                    "sans-serif"
                ),
            ),
        ),

        # ----------------------------------------------------
        # INTERACTION
        # ----------------------------------------------------

        hovermode="closest",
    )


    if showlegend is not None:
        layout_updates["showlegend"] = showlegend


    fig.update_layout(
        **layout_updates
    )


    # --------------------------------------------------------
    # X AXIS
    # --------------------------------------------------------

    fig.update_xaxes(

        showgrid=True,

        gridcolor=GRID,

        gridwidth=1,

        zeroline=False,

        linecolor="rgba(148,163,184,0.14)",

        tickfont=dict(
            color=MUTED,
            size=11,
        ),

        title_font=dict(
            color=MUTED,
            size=11,
        ),

        automargin=True,
    )


    # --------------------------------------------------------
    # Y AXIS
    # --------------------------------------------------------

    fig.update_yaxes(

        showgrid=True,

        gridcolor=GRID,

        gridwidth=1,

        zeroline=False,

        linecolor="rgba(148,163,184,0.14)",

        tickfont=dict(
            color=MUTED,
            size=11,
        ),

        title_font=dict(
            color=MUTED,
            size=11,
        ),

        automargin=True,
    )


    return fig


# ============================================================
# COMPLETION VS REMAINING
# ============================================================

def fig_scope_completion(
    summary: pd.DataFrame,
):

    if summary is None or summary.empty:

        return _layout(
            go.Figure(),
            height=410,
            showlegend=False,
        )


    work = (
        summary
        .copy()
        .sort_values(
            "Completion %",
            ascending=True,
        )
    )


    fig = go.Figure()


    # --------------------------------------------------------
    # APPROVED
    # --------------------------------------------------------

    fig.add_trace(

        go.Bar(

            y=work["Project"],

            x=work["Approved"],

            name="Approved",

            orientation="h",

            marker=dict(
                color=GREEN,
                line=dict(
                    width=0,
                ),
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Approved: %{x:,}"
                "<extra></extra>"
            ),
        )
    )


    # --------------------------------------------------------
    # REMAINING
    # --------------------------------------------------------

    fig.add_trace(

        go.Bar(

            y=work["Project"],

            x=work["Remaining"],

            name="Remaining",

            orientation="h",

            marker=dict(
                color="#26364B",
                line=dict(
                    width=0,
                ),
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Remaining: %{x:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        barmode="stack",

        title="Completion vs Remaining Scope",

        xaxis_title="Records",

        yaxis_title="",

        bargap=0.34,
    )


    return _layout(
        fig,
        height=420,
        legend_y=1.02,
    )


# ============================================================
# QA STATUS DONUT
# ============================================================

def fig_status_mix(
    approved: int,
    rejected: int,
    pending: int,
):

    labels = [
        "Approved",
        "Rejected",
        "Pending",
    ]


    values = [
        approved,
        rejected,
        pending,
    ]


    total = sum(
        values
    )


    fig = go.Figure(

        go.Pie(

            labels=labels,

            values=values,

            hole=0.72,

            sort=False,

            direction="clockwise",

            marker=dict(

                colors=[
                    GREEN,
                    RED,
                    AMBER,
                ],

                line=dict(
                    color="#07111F",
                    width=3,
                ),
            ),

            textinfo="percent",

            textfont=dict(
                color=TEXT,
                size=11,
            ),

            hovertemplate=(
                "<b>%{label}</b>"
                "<br>"
                "%{value:,} records"
                "<br>"
                "%{percent}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title="Portfolio QA Status",

        annotations=[

            dict(

                text=(
                    f"<b>{total:,}</b>"
                    "<br>"
                    "<span style='"
                    "font-size:11px;"
                    "color:#90A2B9"
                    "'>"
                    "received"
                    "</span>"
                ),

                x=0.5,

                y=0.5,

                showarrow=False,

                font=dict(
                    color=TEXT,
                    size=22,
                ),
            )
        ],
    )


    return _layout(
        fig,
        height=420,
        legend_y=1.02,
    )


# ============================================================
# SPEEDOMETER
# ============================================================

def fig_speedometer(
    value,
    title="Completion",
):

    value = max(
        0,
        min(
            float(value),
            1,
        ),
    )


    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=value * 100,

            number=dict(

                suffix="%",

                font=dict(
                    size=38,
                    color=TEXT,
                ),
            ),

            gauge=dict(

                axis=dict(
                    range=[
                        0,
                        100,
                    ],

                    tickcolor=MUTED,

                    tickfont=dict(
                        color=MUTED,
                    ),

                    tickwidth=0,
                ),

                bar=dict(
                    color=BLUE,
                    thickness=0.25,
                ),

                bgcolor="#0A1728",

                borderwidth=0,

                steps=[

                    dict(
                        range=[
                            0,
                            25,
                        ],
                        color="#341B28",
                    ),

                    dict(
                        range=[
                            25,
                            50,
                        ],
                        color="#3A2B18",
                    ),

                    dict(
                        range=[
                            50,
                            75,
                        ],
                        color="#19344A",
                    ),

                    dict(
                        range=[
                            75,
                            100,
                        ],
                        color="#173427",
                    ),
                ],

                threshold=dict(

                    line=dict(
                        color=CYAN,
                        width=3,
                    ),

                    thickness=0.75,

                    value=value * 100,
                ),
            ),

            title=dict(

                text=title,

                font=dict(
                    size=17,
                    color=TEXT,
                ),
            ),
        )
    )


    return _layout(
        fig,
        height=420,
        showlegend=False,
    )


# ============================================================
# MONTHLY TREND
# ============================================================

def fig_monthly_trend(
    monthly: pd.DataFrame,
    title="Monthly Collection & QA Trend",
):

    fig = go.Figure()


    colors = {

        "Received": BLUE,

        "Approved": GREEN,

        "Rejected": RED,

        "Pending": AMBER,
    }


    for column in [
        "Received",
        "Approved",
        "Rejected",
        "Pending",
    ]:

        if column not in monthly.columns:
            continue


        fig.add_trace(

            go.Scatter(

                x=monthly[
                    "Month"
                ],

                y=monthly[
                    column
                ],

                mode=(
                    "lines+markers"
                ),

                name=column,

                line=dict(

                    width=3,

                    color=colors[
                        column
                    ],

                    shape="spline",

                    smoothing=0.55,
                ),

                marker=dict(

                    size=7,

                    color=colors[
                        column
                    ],

                    line=dict(
                        width=1.5,
                        color="#07111F",
                    ),
                ),

                fill=(
                    "tozeroy"
                    if column
                    == "Received"
                    else None
                ),

                fillcolor=(
                    "rgba(59,130,246,0.055)"
                    if column
                    == "Received"
                    else None
                ),

                hovertemplate=(
                    "<b>%{x|%b %Y}</b>"
                    "<br>"
                    + column
                    + ": %{y:,}"
                    "<extra></extra>"
                ),
            )
        )


    fig.update_layout(

        title=title,

        xaxis_title="",

        yaxis_title="Records",

        hovermode="x unified",
    )


    return _layout(
        fig,
        height=440,
        legend_y=1.02,
    )


# ============================================================
# PROJECT HEALTH MATRIX
# ============================================================

def fig_project_health_matrix(
    summary: pd.DataFrame,
):

    if summary is None or summary.empty:

        return _layout(
            go.Figure(),
            height=440,
            showlegend=False,
        )


    metrics = [

        "Completion %",

        "Approval Rate %",

        "QC Reviewed %",

        "Rejection Rate %",

        "Backlog %",
    ]


    z = (
        summary[
            metrics
        ]
        .to_numpy(
            dtype=float
        )
    )


    # Convert risk metrics so high score = better.
    display = (
        z.copy()
    )


    display[:, 3] = (
        1
        - display[:, 3]
    )


    display[:, 4] = (
        1
        - display[:, 4]
    )


    text = [

        [
            f"{value:.1%}"
            for value
            in row
        ]

        for row
        in z
    ]


    fig = go.Figure(

        go.Heatmap(

            z=display,

            x=[
                "Completion",
                "Approval",
                "QC Reviewed",
                "Low Rejection",
                "Low Backlog",
            ],

            y=summary[
                "Project"
            ],

            text=text,

            texttemplate=(
                "%{text}"
            ),

            textfont=dict(
                color="#FFFFFF",
                size=11,
            ),

            colorscale=[

                [
                    0,
                    "#7F1D1D",
                ],

                [
                    0.45,
                    "#D97706",
                ],

                [
                    1,
                    "#15803D",
                ],
            ],

            zmin=0,

            zmax=1,

            colorbar=dict(

                title="Health",

                tickfont=dict(
                    color=MUTED,
                ),

                titlefont=dict(
                    color=MUTED,
                ),

                thickness=10,

                len=0.75,
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "%{x}: %{text}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title="Portfolio Health Matrix",

        xaxis_title="",

        yaxis_title="",
    )


    return _layout(
        fig,
        height=450,
        showlegend=False,
    )


# ============================================================
# PROJECT RADAR
# ============================================================

def fig_project_radar(
    summary: pd.DataFrame,
):

    if summary is None or summary.empty:

        return _layout(
            go.Figure(),
            height=450,
            showlegend=False,
        )


    fig = go.Figure()


    theta = [

        "Completion",

        "Approval",

        "QC Reviewed",

        "Low Rejection",

        "Low Backlog",
    ]


    colors = [

        BLUE,

        GREEN,

        CYAN,

        PURPLE,

        AMBER,

        "#14B8A6",
    ]


    for index, row in summary.iterrows():

        values = [

            row[
                "Completion %"
            ],

            row[
                "Approval Rate %"
            ],

            row[
                "QC Reviewed %"
            ],

            (
                1
                - row[
                    "Rejection Rate %"
                ]
            ),

            (
                1
                - row[
                    "Backlog %"
                ]
            ),
        ]


        fig.add_trace(

            go.Scatterpolar(

                r=(
                    values
                    + [
                        values[0]
                    ]
                ),

                theta=(
                    theta
                    + [
                        theta[0]
                    ]
                ),

                fill="toself",

                opacity=0.18,

                name=row[
                    "Project"
                ],

                line=dict(

                    width=2,

                    color=colors[
                        index
                        % len(colors)
                    ],
                ),
            )
        )


    fig.update_layout(

        title=(
            "Project Performance Radar"
        ),

        polar=dict(

            bgcolor=(
                "rgba(0,0,0,0)"
            ),

            radialaxis=dict(

                range=[
                    0,
                    1,
                ],

                tickformat=".0%",

                gridcolor=GRID,

                linecolor=GRID,

                tickfont=dict(
                    color=MUTED,
                    size=10,
                ),
            ),

            angularaxis=dict(

                gridcolor=GRID,

                linecolor=GRID,

                tickfont=dict(
                    color=MUTED,
                    size=10,
                ),
            ),
        ),
    )


    return _layout(
        fig,
        height=470,
        legend_y=1.02,
    )


# ============================================================
# PORTFOLIO TREEMAP
# ============================================================

def fig_treemap(
    summary: pd.DataFrame,
):

    if summary is None or summary.empty:

        return _layout(
            go.Figure(),
            height=450,
            showlegend=False,
        )


    work = (
        summary.copy()
    )


    fig = px.treemap(

        work,

        path=[
            "Project"
        ],

        values="Scope",

        color=(
            "Completion %"
        ),

        color_continuous_scale=[
            "#7F1D1D",
            "#D97706",
            "#15803D",
        ],

        hover_data=[

            "Received",

            "Approved",

            "Rejected",

            (
                "Pending / "
                "Unreviewed"
            ),
        ],
    )


    fig.update_layout(

        title=(
            "Portfolio Scope & Completion Treemap"
        ),

        coloraxis_colorbar=dict(
            title="Completion",
            tickformat=".0%",
        ),
    )


    return _layout(
        fig,
        height=470,
        showlegend=False,
    )


# ============================================================
# REMAINING SCOPE WATERFALL
# ============================================================

def fig_waterfall(
    summary: pd.DataFrame,
):

    if summary is None or summary.empty:

        return _layout(
            go.Figure(),
            height=440,
            showlegend=False,
        )


    work = (
        summary.copy()
    )


    fig = go.Figure(

        go.Waterfall(

            name="Remaining",

            orientation="v",

            x=work[
                "Project"
            ],

            y=work[
                "Remaining"
            ],

            measure=[
                "relative"
            ]
            * len(work),

            connector=dict(

                line=dict(
                    color=GRID,
                    width=1,
                ),
            ),

            increasing=dict(

                marker=dict(
                    color=PURPLE,
                ),
            ),

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "Remaining: %{y:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title=(
            "Remaining Scope Pressure"
        ),

        yaxis_title=(
            "Remaining approvals"
        ),

        xaxis_title="",
    )


    return _layout(
        fig,
        height=450,
        showlegend=False,
    )


# ============================================================
# DELIVERY FUNNEL
# ============================================================

def fig_funnel(
    summary: pd.DataFrame,
):

    if summary is None or summary.empty:

        return _layout(
            go.Figure(),
            height=450,
            showlegend=False,
        )


    total_scope = (
        summary[
            "Scope"
        ].sum()
    )


    total_received = (
        summary[
            "Received"
        ].sum()
    )


    total_reviewed = (

        summary[
            "Approved"
        ].sum()

        +

        summary[
            "Rejected"
        ].sum()
    )


    total_approved = (
        summary[
            "Approved"
        ].sum()
    )


    fig = go.Figure(

        go.Funnel(

            y=[

                "Scope",

                "Received",

                "QC Reviewed",

                "Approved",
            ],

            x=[

                total_scope,

                total_received,

                total_reviewed,

                total_approved,
            ],

            textinfo=(
                "value+percent initial"
            ),

            textfont=dict(
                color="#FFFFFF",
                size=12,
            ),

            marker=dict(

                color=[

                    SLATE,

                    BLUE,

                    CYAN,

                    GREEN,
                ],
            ),

            connector=dict(

                line=dict(
                    color=GRID,
                    width=1,
                ),
            ),
        )
    )


    fig.update_layout(

        title=(
            "Portfolio Delivery Funnel"
        ),
    )


    return _layout(
        fig,
        height=450,
        showlegend=False,
    )


# ============================================================
# PROVINCE STATUS MIX
# ============================================================

def fig_province_status(
    province_data: pd.DataFrame,
    title="Province Status Mix",
):

    if (
        province_data is None
        or province_data.empty
    ):

        return _layout(
            go.Figure(),
            height=490,
            showlegend=False,
        )


    work = (

        province_data
        .sort_values(
            "Received",
            ascending=True,
        )
        .tail(18)
    )


    fig = go.Figure()


    for column, color in [

        (
            "Approved",
            GREEN,
        ),

        (
            "Rejected",
            RED,
        ),

        (
            "Pending",
            AMBER,
        ),
    ]:

        fig.add_trace(

            go.Bar(

                y=work[
                    "Province"
                ],

                x=work[
                    column
                ],

                name=column,

                orientation="h",

                marker=dict(
                    color=color,
                ),

                hovertemplate=(
                    "<b>%{y}</b>"
                    "<br>"
                    + column
                    + ": %{x:,}"
                    "<extra></extra>"
                ),
            )
        )


    fig.update_layout(

        barmode="stack",

        title=title,

        xaxis_title="Records",

        yaxis_title="",

        bargap=0.26,
    )


    return _layout(
        fig,
        height=520,
        legend_y=1.02,
    )


# ============================================================
# PROVINCE QUALITY / VOLUME
# ============================================================

def fig_province_quality_scatter(
    province_quality: pd.DataFrame,
):

    if (
        province_quality is None
        or province_quality.empty
    ):

        return _layout(
            go.Figure(),
            height=480,
            showlegend=False,
        )


    fig = px.scatter(

        province_quality,

        x="Received",

        y="Quality Index",

        size="Received",

        color=(
            "Rejection Rate %"
        ),

        hover_name=(
            "Province"
        ),

        hover_data=[

            "Approved",

            "Rejected",

            "Pending",

            "Approval Rate %",

            "Backlog %",
        ],

        color_continuous_scale=[

            "#22C55E",

            "#F59E0B",

            "#EF4444",
        ],

        size_max=45,
    )


    fig.update_layout(

        title=(
            "Province Quality vs Volume"
        ),

        yaxis_tickformat=".0%",

        coloraxis_colorbar=dict(
            title="Rejection",
            tickformat=".0%",
        ),
    )


    return _layout(
        fig,
        height=490,
        showlegend=False,
    )


# ============================================================
# REJECTION PARETO
# ============================================================

def fig_rejection_pareto(
    reasons: pd.DataFrame,
    title="Top Rejection Reasons",
):

    if (
        reasons is None
        or reasons.empty
    ):

        fig = go.Figure()


        fig.add_annotation(

            text=(
                "No rejected records "
                "in the current view"
            ),

            showarrow=False,

            font=dict(
                color=MUTED,
                size=13,
            ),
        )


        fig.update_layout(
            title=title
        )


        return _layout(
            fig,
            height=470,
            showlegend=False,
        )


    work = (
        reasons
        .sort_values(
            "Count",
            ascending=True,
        )
    )


    fig = go.Figure(

        go.Bar(

            y=work[
                "Reason"
            ],

            x=work[
                "Count"
            ],

            orientation="h",

            marker=dict(

                color=work[
                    "Count"
                ],

                colorscale=[

                    [
                        0,
                        "#4338CA",
                    ],

                    [
                        0.5,
                        "#7C3AED",
                    ],

                    [
                        1,
                        RED,
                    ],
                ],
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Rejected: %{x:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title=title,

        xaxis_title=(
            "Rejected records"
        ),

        yaxis_title="",

        bargap=0.22,
    )


    fig.update_yaxes(
        automargin=True
    )


    return _layout(

        fig,

        height=540,

        margin=dict(
            l=24,
            r=20,
            t=105,
            b=30,
        ),

        showlegend=False,
    )


# ============================================================
# VT TOOL RISK MAP
# ============================================================

def fig_vt_tool_bubble(
    vt_summary: pd.DataFrame,
):

    if (
        vt_summary is None
        or vt_summary.empty
    ):

        return _layout(
            go.Figure(),
            height=460,
            showlegend=False,
        )


    work = (
        vt_summary.copy()
    )


    work[
        "Bubble"
    ] = np.maximum(
        work[
            "Received"
        ],
        10,
    )


    fig = px.scatter(

        work,

        x=(
            "Approval Rate %"
        ),

        y=(
            "Rejection Rate %"
        ),

        size="Bubble",

        color="Backlog %",

        hover_name=(
            "VT Tool Type"
        ),

        hover_data={

            "Received": True,

            "Approved": True,

            "Rejected": True,

            "Pending": True,

            "Bubble": False,
        },

        color_continuous_scale=[

            "#22C55E",

            "#F59E0B",

            "#EF4444",
        ],

        size_max=52,
    )


    fig.update_layout(

        title="VT Tool Risk Map",

        xaxis_tickformat=".0%",

        yaxis_tickformat=".0%",

        coloraxis_colorbar=dict(

            title="Backlog",

            tickformat=".0%",
        ),
    )


    return _layout(
        fig,
        height=470,
        showlegend=False,
    )


# ============================================================
# FIELD STAFF PERFORMANCE
# ============================================================

def fig_staff_scatter(
    staff: pd.DataFrame,
):

    if (
        staff is None
        or staff.empty
    ):

        return _layout(
            go.Figure(),
            height=500,
            showlegend=False,
        )


    fig = px.scatter(

        staff,

        x="Received",

        y=(
            "Approval Rate %"
        ),

        size="Received",

        color=(
            "Rejection Rate %"
        ),

        hover_name=(
            "Field Staff"
        ),

        hover_data=[

            "Approved",

            "Rejected",

            "Pending",
        ],

        color_continuous_scale=[

            "#22C55E",

            "#F59E0B",

            "#EF4444",
        ],

        size_max=40,
    )


    fig.update_layout(

        title=(
            "Field Staff Performance Map "
            "(Pseudonymized)"
        ),

        yaxis_tickformat=".0%",

        coloraxis_colorbar=dict(

            title="Rejection",

            tickformat=".0%",
        ),
    )


    return _layout(
        fig,
        height=520,
        showlegend=False,
    )


# ============================================================
# QA REVIEWER WORKLOAD
# ============================================================

def fig_qc_reviewer(
    qc: pd.DataFrame,
):

    if (
        qc is None
        or qc.empty
    ):

        return _layout(
            go.Figure(),
            height=450,
            showlegend=False,
        )


    work = (

        qc
        .sort_values(
            "Reviewed",
            ascending=True,
        )
        .tail(15)
    )


    fig = go.Figure()


    fig.add_trace(

        go.Bar(

            y=work[
                "QA Reviewer"
            ],

            x=work[
                "Approved"
            ],

            name="Approved",

            orientation="h",

            marker=dict(
                color=GREEN,
            ),
        )
    )


    fig.add_trace(

        go.Bar(

            y=work[
                "QA Reviewer"
            ],

            x=work[
                "Rejected"
            ],

            name="Rejected",

            orientation="h",

            marker=dict(
                color=RED,
            ),
        )
    )


    fig.update_layout(

        barmode="stack",

        title=(
            "QA Reviewer Workload & Outcomes"
        ),

        xaxis_title=(
            "Reviewed records"
        ),

        yaxis_title="",

        bargap=0.26,
    )


    return _layout(
        fig,
        height=480,
        legend_y=1.02,
    )


# ============================================================
# GENERIC CATEGORY BAR
# ============================================================

def fig_category_bar(
    data: pd.DataFrame,
    category: str,
    value: str,
    title: str,
):

    if (
        data is None
        or data.empty
    ):

        return _layout(
            go.Figure(),
            height=410,
            showlegend=False,
        )


    work = (

        data
        .sort_values(
            value,
            ascending=True,
        )
        .tail(15)
    )


    fig = go.Figure(

        go.Bar(

            y=work[
                category
            ],

            x=work[
                value
            ],

            orientation="h",

            marker=dict(

                color=work[
                    value
                ],

                colorscale=[

                    [
                        0,
                        "#1D4ED8",
                    ],

                    [
                        1,
                        CYAN,
                    ],
                ],
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Records: %{x:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title=title,

        xaxis_title="Records",

        yaxis_title="",

        bargap=0.24,
    )


    return _layout(
        fig,
        height=440,
        showlegend=False,
    )


# ============================================================
# MORAA SUNBURST
# ============================================================

def fig_sunburst(
    data: pd.DataFrame,
    level1: str,
    level2: str,
    level3: str,
):

    if (
        data is None
        or data.empty
    ):

        return _layout(
            go.Figure(),
            height=470,
            showlegend=False,
        )


    work = (
        data
        .copy()
        .replace(
            "",
            "Unknown",
        )
        .fillna(
            "Unknown"
        )
    )


    fig = px.sunburst(

        work,

        path=[

            level1,

            level2,

            level3,
        ],

        color=level3,

        color_discrete_map={

            "Approved": GREEN,

            "Rejected": RED,

            "Pending": AMBER,

            "Unreviewed": SLATE,
        },
    )


    fig.update_layout(

        title=(
            "Moraa Phase → "
            "Discipline → QA Status"
        ),
    )


    return _layout(
        fig,
        height=490,
        showlegend=False,
    )


# ============================================================
# QA COMPONENT PROFILE
# ============================================================

def fig_quality_components(
    quality: pd.DataFrame,
    title="QA Component Profile",
):

    if (
        quality is None
        or quality.empty
    ):

        fig = go.Figure()


        fig.add_annotation(

            text=(
                "No numeric component scores "
                "are available in this view"
            ),

            showarrow=False,

            font=dict(
                color=MUTED,
                size=13,
            ),
        )


        fig.update_layout(
            title=title
        )


        return _layout(
            fig,
            height=440,
            showlegend=False,
        )


    chart_colors = [

        BLUE,

        PURPLE,

        CYAN,

        GREEN,

        AMBER,
    ]


    fig = go.Figure(

        go.Bar(

            x=quality[
                "Metric"
            ],

            y=quality[
                "Average"
            ],

            marker_color=(
                chart_colors[
                    : len(quality)
                ]
            ),

            text=[

                f"{value:.2f}"

                for value
                in quality[
                    "Average"
                ]
            ],

            textposition=(
                "outside"
            ),

            textfont=dict(
                color=TEXT,
                size=11,
            ),

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "Average: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title=title,

        xaxis_title="",

        yaxis_title=(
            "Average score"
        ),
    )


    return _layout(
        fig,
        height=450,
        showlegend=False,
    )


# ============================================================
# CALENDAR / COLLECTION INTENSITY HEATMAP
# ============================================================

def fig_calendar_heatmap(
    calendar_data: pd.DataFrame,
):

    if (
        calendar_data is None
        or calendar_data.empty
    ):

        return _layout(
            go.Figure(),
            height=440,
            showlegend=False,
        )


    work = (
        calendar_data.copy()
    )


    weekday_order = [

        "Monday",

        "Tuesday",

        "Wednesday",

        "Thursday",

        "Friday",

        "Saturday",

        "Sunday",
    ]


    month_order = [

        "Jan",

        "Feb",

        "Mar",

        "Apr",

        "May",

        "Jun",

        "Jul",

        "Aug",

        "Sep",

        "Oct",

        "Nov",

        "Dec",
    ]


    pivot = (
        work
        .pivot_table(

            index="Weekday",

            columns="Month",

            values="Records",

            aggfunc="sum",

            fill_value=0,
        )
        .reindex(

            index=weekday_order,

            columns=month_order,

            fill_value=0,
        )
    )


    fig = go.Figure(

        go.Heatmap(

            z=pivot.values,

            x=pivot.columns,

            y=pivot.index,

            colorscale=[

                [
                    0,
                    "#0B192B",
                ],

                [
                    0.35,
                    "#1D4ED8",
                ],

                [
                    1,
                    "#22D3EE",
                ],
            ],

            colorbar=dict(

                title="Records",

                thickness=10,

                len=0.78,

                tickfont=dict(
                    color=MUTED,
                ),
            ),

            text=pivot.values,

            texttemplate=(
                "%{text}"
            ),

            textfont=dict(
                color="#FFFFFF",
                size=10,
            ),

            hovertemplate=(
                "<b>%{y} • %{x}</b>"
                "<br>"
                "Records: %{z:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title=(
            "Collection Intensity Heatmap"
        ),
    )


    return _layout(
        fig,
        height=450,
        showlegend=False,
    )

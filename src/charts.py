from __future__ import annotations

import textwrap

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
# SAFE HELPERS
# ============================================================

def _is_empty(data) -> bool:
    """
    Safely test if a dataframe-like object is empty.
    """

    if data is None:
        return True

    try:
        return data.empty
    except Exception:
        return False


def _safe_numeric(
    series: pd.Series,
    default: float = 0.0,
) -> pd.Series:
    """
    Convert a pandas series to numeric values without raising errors.
    """

    return (
        pd.to_numeric(
            series,
            errors="coerce",
        )
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(default)
    )


def _safe_percent(
    series: pd.Series,
) -> pd.Series:
    """
    Convert a series to safe percentage ratios between 0 and 1.
    """

    return (
        _safe_numeric(series)
        .clip(
            lower=0,
            upper=1,
        )
    )


def _has_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> bool:
    """
    Verify that all required columns exist.
    """

    if _is_empty(df):
        return False

    return all(
        column in df.columns
        for column in columns
    )


def _short_text(
    value,
    width: int = 72,
) -> str:
    """
    Shorten long labels for chart axes while keeping them readable.
    """

    text = str(value or "").strip()

    if not text:
        return "Unknown"

    return textwrap.shorten(
        text,
        width=width,
        placeholder="…",
    )


def _colorbar(
    title: str,
    *,
    percent: bool = False,
    length: float = 0.72,
) -> dict:
    """
    Return a Plotly-compatible colorbar configuration.

    IMPORTANT:
    Do not use `titlefont`.
    Modern Plotly expects:
        title=dict(text="...", font=dict(...))
    """

    config = dict(

        title=dict(
            text=title,
            font=dict(
                color=MUTED,
                size=11,
            ),
        ),

        tickfont=dict(
            color=MUTED,
            size=10,
        ),

        thickness=10,

        len=length,

        outlinewidth=0,

        bgcolor="rgba(0,0,0,0)",
    )

    if percent:
        config["tickformat"] = ".0%"

    return config


# ============================================================
# EMPTY FIGURE
# ============================================================

def _empty_figure(
    title: str,
    message: str = "No data available for the current selection.",
    *,
    height: int = 420,
):
    """
    Create a consistent empty-state chart.
    """

    fig = go.Figure()

    fig.update_layout(
        title=title,
    )

    fig.add_annotation(

        x=0.5,
        y=0.48,

        xref="paper",
        yref="paper",

        text=message,

        showarrow=False,

        align="center",

        font=dict(
            color=MUTED,
            size=13,
        ),
    )

    return _layout(
        fig,
        height=height,
        showlegend=False,
        top_margin=92,
    )


# ============================================================
# GLOBAL LAYOUT
# ============================================================

def _layout(
    fig,
    height: int = 420,
    margin: dict | None = None,
    *,
    showlegend: bool | None = None,
    legend_y: float = 1.02,
    top_margin: int = 112,
):
    """
    Global visual system for every Plotly chart.

    Title and legend receive separate visual space so they do not
    collide, particularly on laptop displays.
    """

    layout_settings = dict(

        height=height,

        paper_bgcolor=BG,

        plot_bgcolor=BG,

        font=dict(
            family="Inter, Segoe UI, Arial, sans-serif",
            color=TEXT,
            size=12,
        ),

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title=dict(

            x=0.02,

            y=0.985,

            xanchor="left",

            yanchor="top",

            font=dict(
                family="Inter, Segoe UI, Arial, sans-serif",
                color=TEXT_BRIGHT,
                size=17,
            ),

            pad=dict(
                t=2,
                b=14,
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
                t=top_margin,
                b=30,
            )
        ),

        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        legend=dict(

            orientation="h",

            x=0.02,

            y=legend_y,

            xanchor="left",

            yanchor="bottom",

            font=dict(
                color=MUTED,
                size=11,
            ),

            bgcolor="rgba(0,0,0,0)",

            borderwidth=0,

            tracegroupgap=8,

            itemclick="toggle",

            itemdoubleclick="toggleothers",
        ),

        # ----------------------------------------------------
        # HOVER
        # ----------------------------------------------------

        hoverlabel=dict(

            bgcolor=NAVY,

            bordercolor="#1E334D",

            font=dict(
                family="Inter, Segoe UI, Arial, sans-serif",
                color="#FFFFFF",
                size=12,
            ),
        ),
    )


    if showlegend is not None:
        layout_settings["showlegend"] = showlegend


    fig.update_layout(
        **layout_settings
    )


    # --------------------------------------------------------
    # AXIS STYLE
    # --------------------------------------------------------

    fig.update_xaxes(

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


    fig.update_yaxes(

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
# COMPLETION VS REMAINING SCOPE
# ============================================================

def fig_scope_completion(
    summary: pd.DataFrame,
):

    required = [
        "Project",
        "Approved",
        "Remaining",
        "Completion %",
    ]


    if not _has_columns(
        summary,
        required,
    ):
        return _empty_figure(
            "Completion vs Remaining Scope"
        )


    work = summary.copy()


    work["Approved"] = (
        _safe_numeric(
            work["Approved"]
        )
    )


    work["Remaining"] = (
        _safe_numeric(
            work["Remaining"]
        )
    )


    work["Completion %"] = (
        _safe_percent(
            work["Completion %"]
        )
    )


    work = (
        work
        .sort_values(
            "Completion %",
            ascending=True,
        )
    )


    fig = go.Figure()


    fig.add_trace(

        go.Bar(

            y=work[
                "Project"
            ],

            x=work[
                "Approved"
            ],

            name="Approved",

            orientation="h",

            marker=dict(
                color=GREEN,
            ),

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Approved: %{x:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.add_trace(

        go.Bar(

            y=work[
                "Project"
            ],

            x=work[
                "Remaining"
            ],

            name="Remaining",

            orientation="h",

            marker=dict(
                color="#26364B",
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

        title=(
            "Completion vs Remaining Scope"
        ),

        barmode="stack",

        bargap=0.34,

        xaxis_title="Records",

        yaxis_title="",
    )


    return _layout(
        fig,
        height=430,
        legend_y=1.02,
        top_margin=118,
    )


# ============================================================
# QA STATUS DONUT
# ============================================================

def fig_status_mix(
    approved: int,
    rejected: int,
    pending: int,
):

    approved = max(
        float(approved or 0),
        0,
    )

    rejected = max(
        float(rejected or 0),
        0,
    )

    pending = max(
        float(pending or 0),
        0,
    )


    values = [
        approved,
        rejected,
        pending,
    ]


    total = sum(
        values
    )


    if total <= 0:

        return _empty_figure(
            "Portfolio QA Status",
            "No QA status records are available.",
        )


    fig = go.Figure(

        go.Pie(

            labels=[
                "Approved",
                "Rejected",
                "Pending",
            ],

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

        title=(
            "Portfolio QA Status"
        ),

        annotations=[

            dict(

                x=0.5,

                y=0.5,

                text=(
                    f"<b>{total:,.0f}</b>"
                    "<br>"
                    "<span style='"
                    "font-size:11px;"
                    "color:#90A2B9"
                    "'>"
                    "received"
                    "</span>"
                ),

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
        height=430,
        legend_y=1.02,
        top_margin=118,
    )


# ============================================================
# SPEEDOMETER
# ============================================================

def fig_speedometer(
    value,
    title="Completion",
):

    try:
        value = float(value)
    except Exception:
        value = 0.0


    if not np.isfinite(value):
        value = 0.0


    value = max(
        0,
        min(
            value,
            1,
        ),
    )


    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=(
                value
                * 100
            ),

            number=dict(

                suffix="%",

                valueformat=".1f",

                font=dict(
                    size=38,
                    color=TEXT,
                ),
            ),

            title=dict(

                text=title,

                font=dict(
                    size=17,
                    color=TEXT_BRIGHT,
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
                        size=10,
                    ),
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

                    value=(
                        value
                        * 100
                    ),
                ),
            ),
        )
    )


    return _layout(

        fig,

        height=430,

        showlegend=False,

        top_margin=70,

        margin=dict(
            l=25,
            r=25,
            t=70,
            b=20,
        ),
    )


# ============================================================
# MONTHLY TREND
# ============================================================

def fig_monthly_trend(
    monthly: pd.DataFrame,
    title="Monthly Collection & QA Trend",
):

    required = [
        "Month",
        "Received",
        "Approved",
        "Rejected",
        "Pending",
    ]


    if not _has_columns(
        monthly,
        required,
    ):
        return _empty_figure(
            title
        )


    work = (
        monthly.copy()
    )


    colors = {

        "Received": BLUE,

        "Approved": GREEN,

        "Rejected": RED,

        "Pending": AMBER,
    }


    fig = go.Figure()


    for column in [
        "Received",
        "Approved",
        "Rejected",
        "Pending",
    ]:

        values = (
            _safe_numeric(
                work[column]
            )
        )


        fig.add_trace(

            go.Scatter(

                x=work[
                    "Month"
                ],

                y=values,

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

                    smoothing=0.45,
                ),

                marker=dict(

                    size=7,

                    color=colors[
                        column
                    ],

                    line=dict(
                        width=1,
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


    result = _layout(
        fig,
        height=450,
        legend_y=1.02,
        top_margin=118,
    )


    result.update_layout(
        hovermode="x unified"
    )


    return result


# ============================================================
# PROJECT HEALTH MATRIX
# ============================================================

def fig_project_health_matrix(
    summary: pd.DataFrame,
):

    required = [

        "Project",

        "Completion %",

        "Approval Rate %",

        "QC Reviewed %",

        "Rejection Rate %",

        "Backlog %",
    ]


    if not _has_columns(
        summary,
        required,
    ):

        return _empty_figure(
            "Portfolio Health Matrix"
        )


    matrix = pd.DataFrame(

        {
            "Completion %": (
                _safe_percent(
                    summary[
                        "Completion %"
                    ]
                )
            ),

            "Approval Rate %": (
                _safe_percent(
                    summary[
                        "Approval Rate %"
                    ]
                )
            ),

            "QC Reviewed %": (
                _safe_percent(
                    summary[
                        "QC Reviewed %"
                    ]
                )
            ),

            "Rejection Rate %": (
                _safe_percent(
                    summary[
                        "Rejection Rate %"
                    ]
                )
            ),

            "Backlog %": (
                _safe_percent(
                    summary[
                        "Backlog %"
                    ]
                )
            ),
        }
    )


    raw_values = (
        matrix
        .to_numpy(
            dtype=float
        )
    )


    health_values = (
        raw_values.copy()
    )


    # Lower rejection is healthier.
    health_values[:, 3] = (
        1
        - health_values[:, 3]
    )


    # Lower backlog is healthier.
    health_values[:, 4] = (
        1
        - health_values[:, 4]
    )


    text_values = [

        [
            f"{value:.1%}"
            for value
            in row
        ]

        for row
        in raw_values
    ]


    project_labels = (

        summary[
            "Project"
        ]
        .fillna(
            "Unknown"
        )
        .astype(str)
        .tolist()
    )


    fig = go.Figure()


    heatmap = go.Heatmap(

        z=health_values,

        x=[

            "Completion",

            "Approval",

            "QC Reviewed",

            "Low Rejection",

            "Low Backlog",
        ],

        y=project_labels,

        text=text_values,

        texttemplate="%{text}",

        colorscale=[

            [
                0.00,
                "#7F1D1D",
            ],

            [
                0.25,
                "#B91C1C",
            ],

            [
                0.45,
                "#D97706",
            ],

            [
                0.65,
                "#CA8A04",
            ],

            [
                0.80,
                "#16A34A",
            ],

            [
                1.00,
                "#15803D",
            ],
        ],

        zmin=0,

        zmax=1,

        colorbar=dict(

            title=dict(

                text="Health",

                font=dict(
                    color=MUTED,
                    size=11,
                ),
            ),

            tickfont=dict(
                color=MUTED,
                size=10,
            ),

            thickness=10,

            len=0.72,

            x=1.02,

            outlinewidth=0,

            bgcolor=(
                "rgba(0,0,0,0)"
            ),

            tickvals=[
                0,
                0.5,
                1,
            ],

            ticktext=[
                "Weak",
                "Watch",
                "Strong",
            ],
        ),

        hovertemplate=(
            "<b>%{y}</b>"
            "<br>"
            "%{x}: %{text}"
            "<extra></extra>"
        ),

        xgap=3,

        ygap=3,
    )


    fig.add_trace(
        heatmap
    )


    fig.update_layout(

        title=(
            "Portfolio Health Matrix"
        ),

        xaxis_title="",

        yaxis_title="",
    )


    fig.update_xaxes(

        side="top",

        showgrid=False,

        zeroline=False,
    )


    fig.update_yaxes(

        autorange="reversed",

        showgrid=False,

        zeroline=False,
    )


    return _layout(

        fig,

        height=480,

        showlegend=False,

        margin=dict(
            l=100,
            r=90,
            t=105,
            b=35,
        ),
    )


# ============================================================
# PROJECT PERFORMANCE RADAR
# ============================================================

def fig_project_radar(
    summary: pd.DataFrame,
):

    required = [

        "Project",

        "Completion %",

        "Approval Rate %",

        "QC Reviewed %",

        "Rejection Rate %",

        "Backlog %",
    ]


    if not _has_columns(
        summary,
        required,
    ):

        return _empty_figure(
            "Project Performance Radar"
        )


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

        "#E879F9",
    ]


    fig = go.Figure()


    for position, (_, row) in enumerate(
        summary.iterrows()
    ):

        completion = float(
            np.clip(
                pd.to_numeric(
                    row[
                        "Completion %"
                    ],
                    errors="coerce",
                )
                if pd.notna(
                    row[
                        "Completion %"
                    ]
                )
                else 0,
                0,
                1,
            )
        )


        approval = float(
            np.clip(
                pd.to_numeric(
                    row[
                        "Approval Rate %"
                    ],
                    errors="coerce",
                )
                if pd.notna(
                    row[
                        "Approval Rate %"
                    ]
                )
                else 0,
                0,
                1,
            )
        )


        reviewed = float(
            np.clip(
                pd.to_numeric(
                    row[
                        "QC Reviewed %"
                    ],
                    errors="coerce",
                )
                if pd.notna(
                    row[
                        "QC Reviewed %"
                    ]
                )
                else 0,
                0,
                1,
            )
        )


        rejection = float(
            np.clip(
                pd.to_numeric(
                    row[
                        "Rejection Rate %"
                    ],
                    errors="coerce",
                )
                if pd.notna(
                    row[
                        "Rejection Rate %"
                    ]
                )
                else 0,
                0,
                1,
            )
        )


        backlog = float(
            np.clip(
                pd.to_numeric(
                    row[
                        "Backlog %"
                    ],
                    errors="coerce",
                )
                if pd.notna(
                    row[
                        "Backlog %"
                    ]
                )
                else 0,
                0,
                1,
            )
        )


        values = [

            completion,

            approval,

            reviewed,

            1 - rejection,

            1 - backlog,
        ]


        closed_values = (
            values
            + [
                values[0]
            ]
        )


        closed_theta = (
            theta
            + [
                theta[0]
            ]
        )


        fig.add_trace(

            go.Scatterpolar(

                r=closed_values,

                theta=closed_theta,

                fill="toself",

                opacity=0.18,

                name=str(
                    row[
                        "Project"
                    ]
                ),

                line=dict(

                    width=2,

                    color=colors[
                        position
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

        height=480,

        legend_y=1.02,

        top_margin=118,
    )


# ============================================================
# PORTFOLIO TREEMAP
# ============================================================

def fig_treemap(
    summary: pd.DataFrame,
):

    required = [

        "Project",

        "Scope",

        "Completion %",

        "Received",

        "Approved",

        "Rejected",

        "Pending / Unreviewed",
    ]


    if not _has_columns(
        summary,
        required,
    ):

        return _empty_figure(
            "Portfolio Scope & Completion Treemap"
        )


    work = (
        summary.copy()
    )


    work["Scope"] = (
        _safe_numeric(
            work[
                "Scope"
            ]
        )
    )


    work["Completion %"] = (
        _safe_percent(
            work[
                "Completion %"
            ]
        )
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

        coloraxis_colorbar=_colorbar(
            "Completion",
            percent=True,
        ),
    )


    return _layout(

        fig,

        height=470,

        showlegend=False,

        top_margin=90,
    )


# ============================================================
# REMAINING SCOPE PRESSURE
# ============================================================

def fig_waterfall(
    summary: pd.DataFrame,
):

    required = [
        "Project",
        "Remaining",
    ]


    if not _has_columns(
        summary,
        required,
    ):

        return _empty_figure(
            "Remaining Scope Pressure"
        )


    work = (
        summary.copy()
    )


    work["Remaining"] = (
        _safe_numeric(
            work[
                "Remaining"
            ]
        )
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

            decreasing=dict(

                marker=dict(
                    color=CYAN,
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

        xaxis_title="",

        yaxis_title=(
            "Remaining approvals"
        ),
    )


    return _layout(

        fig,

        height=450,

        showlegend=False,

        top_margin=92,
    )


# ============================================================
# PORTFOLIO DELIVERY FUNNEL
# ============================================================

def fig_funnel(
    summary: pd.DataFrame,
):

    required = [

        "Scope",

        "Received",

        "Approved",

        "Rejected",
    ]


    if not _has_columns(
        summary,
        required,
    ):

        return _empty_figure(
            "Portfolio Delivery Funnel"
        )


    total_scope = (
        _safe_numeric(
            summary[
                "Scope"
            ]
        )
        .sum()
    )


    total_received = (
        _safe_numeric(
            summary[
                "Received"
            ]
        )
        .sum()
    )


    total_approved = (
        _safe_numeric(
            summary[
                "Approved"
            ]
        )
        .sum()
    )


    total_rejected = (
        _safe_numeric(
            summary[
                "Rejected"
            ]
        )
        .sum()
    )


    total_reviewed = (
        total_approved
        + total_rejected
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

        top_margin=92,
    )


# ============================================================
# PROVINCE STATUS
# ============================================================

def fig_province_status(
    province_data: pd.DataFrame,
    title="Province Status Mix",
):

    required = [

        "Province",

        "Received",

        "Approved",

        "Rejected",

        "Pending",
    ]


    if not _has_columns(
        province_data,
        required,
    ):

        return _empty_figure(
            title
        )


    work = (
        province_data.copy()
    )


    for column in [

        "Received",

        "Approved",

        "Rejected",

        "Pending",
    ]:

        work[column] = (
            _safe_numeric(
                work[column]
            )
        )


    work = (

        work
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

        title=title,

        barmode="stack",

        bargap=0.27,

        xaxis_title="Records",

        yaxis_title="",
    )


    return _layout(

        fig,

        height=520,

        legend_y=1.02,

        top_margin=118,
    )


# ============================================================
# PROVINCE QUALITY VS VOLUME
# ============================================================

def fig_province_quality_scatter(
    province_quality: pd.DataFrame,
):

    required = [

        "Province",

        "Received",

        "Quality Index",

        "Rejection Rate %",

        "Approved",

        "Rejected",

        "Pending",

        "Approval Rate %",

        "Backlog %",
    ]


    if not _has_columns(
        province_quality,
        required,
    ):

        return _empty_figure(
            "Province Quality vs Volume"
        )


    work = (
        province_quality.copy()
    )


    work["Received"] = (
        _safe_numeric(
            work[
                "Received"
            ]
        )
    )


    work["Quality Index"] = (
        _safe_percent(
            work[
                "Quality Index"
            ]
        )
    )


    work["Rejection Rate %"] = (
        _safe_percent(
            work[
                "Rejection Rate %"
            ]
        )
    )


    work["Bubble Size"] = (
        work[
            "Received"
        ]
        .clip(
            lower=1
        )
    )


    fig = px.scatter(

        work,

        x="Received",

        y="Quality Index",

        size="Bubble Size",

        color=(
            "Rejection Rate %"
        ),

        hover_name="Province",

        hover_data={

            "Bubble Size": False,

            "Approved": True,

            "Rejected": True,

            "Pending": True,

            "Approval Rate %": ":.1%",

            "Backlog %": ":.1%",
        },

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

        coloraxis_colorbar=_colorbar(
            "Rejection",
            percent=True,
        ),
    )


    return _layout(

        fig,

        height=490,

        showlegend=False,

        top_margin=92,
    )


# ============================================================
# REJECTION PARETO
# ============================================================

def fig_rejection_pareto(
    reasons: pd.DataFrame,
    title="Top Rejection Reasons",
):

    required = [
        "Reason",
        "Count",
    ]


    if not _has_columns(
        reasons,
        required,
    ):

        return _empty_figure(

            title,

            "No rejected records are available in the current view.",

            height=500,
        )


    work = (
        reasons.copy()
    )


    work["Count"] = (
        _safe_numeric(
            work[
                "Count"
            ]
        )
    )


    work["Full Reason"] = (
        work[
            "Reason"
        ]
        .fillna(
            "No reason documented"
        )
        .astype(str)
    )


    work["Reason Display"] = (
        work[
            "Full Reason"
        ]
        .map(
            lambda value:
            _short_text(
                value,
                width=78,
            )
        )
    )


    work = (
        work
        .sort_values(
            "Count",
            ascending=True,
        )
    )


    fig = go.Figure(

        go.Bar(

            y=work[
                "Reason Display"
            ],

            x=work[
                "Count"
            ],

            customdata=work[
                "Full Reason"
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
                        0.50,
                        "#7C3AED",
                    ],

                    [
                        1,
                        RED,
                    ],
                ],
            ),

            hovertemplate=(
                "<b>%{customdata}</b>"
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

        bargap=0.24,
    )


    return _layout(

        fig,

        height=560,

        showlegend=False,

        margin=dict(
            l=30,
            r=25,
            t=100,
            b=35,
        ),
    )


# ============================================================
# VT TOOL RISK MAP
# ============================================================

def fig_vt_tool_bubble(
    vt_summary: pd.DataFrame,
):

    required = [

        "VT Tool Type",

        "Received",

        "Approved",

        "Rejected",

        "Pending",

        "Approval Rate %",

        "Rejection Rate %",

        "Backlog %",
    ]


    if not _has_columns(
        vt_summary,
        required,
    ):

        return _empty_figure(
            "VT Tool Risk Map"
        )


    work = (
        vt_summary.copy()
    )


    work["Received"] = (
        _safe_numeric(
            work[
                "Received"
            ]
        )
    )


    work["Approval Rate %"] = (
        _safe_percent(
            work[
                "Approval Rate %"
            ]
        )
    )


    work["Rejection Rate %"] = (
        _safe_percent(
            work[
                "Rejection Rate %"
            ]
        )
    )


    work["Backlog %"] = (
        _safe_percent(
            work[
                "Backlog %"
            ]
        )
    )


    work["Bubble"] = (
        work[
            "Received"
        ]
        .clip(
            lower=10
        )
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

            "Backlog %": ":.1%",
        },

        color_continuous_scale=[

            "#22C55E",

            "#F59E0B",

            "#EF4444",
        ],

        size_max=52,
    )


    fig.update_layout(

        title=(
            "VT Tool Risk Map"
        ),

        xaxis_tickformat=".0%",

        yaxis_tickformat=".0%",

        coloraxis_colorbar=_colorbar(
            "Backlog",
            percent=True,
        ),
    )


    return _layout(

        fig,

        height=480,

        showlegend=False,

        top_margin=92,
    )


# ============================================================
# FIELD STAFF PERFORMANCE
# ============================================================

def fig_staff_scatter(
    staff: pd.DataFrame,
):

    required = [

        "Field Staff",

        "Received",

        "Approved",

        "Rejected",

        "Pending",

        "Approval Rate %",

        "Rejection Rate %",
    ]


    if not _has_columns(
        staff,
        required,
    ):

        return _empty_figure(
            "Field Staff Performance Map (Pseudonymized)"
        )


    work = (
        staff.copy()
    )


    work["Received"] = (
        _safe_numeric(
            work[
                "Received"
            ]
        )
    )


    work["Approval Rate %"] = (
        _safe_percent(
            work[
                "Approval Rate %"
            ]
        )
    )


    work["Rejection Rate %"] = (
        _safe_percent(
            work[
                "Rejection Rate %"
            ]
        )
    )


    work["Bubble"] = (
        work[
            "Received"
        ]
        .clip(
            lower=1
        )
    )


    fig = px.scatter(

        work,

        x="Received",

        y=(
            "Approval Rate %"
        ),

        size="Bubble",

        color=(
            "Rejection Rate %"
        ),

        hover_name=(
            "Field Staff"
        ),

        hover_data={

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

        size_max=40,
    )


    fig.update_layout(

        title=(
            "Field Staff Performance Map (Pseudonymized)"
        ),

        yaxis_tickformat=".0%",

        coloraxis_colorbar=_colorbar(
            "Rejection",
            percent=True,
        ),
    )


    return _layout(

        fig,

        height=520,

        showlegend=False,

        top_margin=92,
    )


# ============================================================
# QA REVIEWER WORKLOAD
# ============================================================

def fig_qc_reviewer(
    qc: pd.DataFrame,
):

    required = [

        "QA Reviewer",

        "Reviewed",

        "Approved",

        "Rejected",
    ]


    if not _has_columns(
        qc,
        required,
    ):

        return _empty_figure(
            "QA Reviewer Workload & Outcomes"
        )


    work = (
        qc.copy()
    )


    for column in [

        "Reviewed",

        "Approved",

        "Rejected",
    ]:

        work[column] = (
            _safe_numeric(
                work[column]
            )
        )


    work = (

        work
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

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Approved: %{x:,}"
                "<extra></extra>"
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

            hovertemplate=(
                "<b>%{y}</b>"
                "<br>"
                "Rejected: %{x:,}"
                "<extra></extra>"
            ),
        )
    )


    fig.update_layout(

        title=(
            "QA Reviewer Workload & Outcomes"
        ),

        barmode="stack",

        bargap=0.27,

        xaxis_title=(
            "Reviewed records"
        ),

        yaxis_title="",
    )


    return _layout(

        fig,

        height=480,

        legend_y=1.02,

        top_margin=118,
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
        _is_empty(data)
        or category not in data.columns
        or value not in data.columns
    ):

        return _empty_figure(
            title
        )


    work = (
        data.copy()
    )


    work[value] = (
        _safe_numeric(
            work[value]
        )
    )


    work[category] = (

        work[
            category
        ]
        .fillna(
            "Unknown"
        )
        .astype(str)
        .replace(
            "",
            "Unknown",
        )
    )


    work = (

        work
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

        bargap=0.25,
    )


    return _layout(

        fig,

        height=450,

        showlegend=False,

        top_margin=92,
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

    required = [
        level1,
        level2,
        level3,
    ]


    if not _has_columns(
        data,
        required,
    ):

        return _empty_figure(
            "Moraa Phase → Discipline → QA Status"
        )


    work = (
        data[
            required
        ]
        .copy()
        .fillna(
            "Unknown"
        )
    )


    for column in required:

        work[column] = (

            work[column]
            .astype(str)
            .str.strip()
            .replace(
                "",
                "Unknown",
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
            "Moraa Phase → Discipline → QA Status"
        ),
    )


    return _layout(

        fig,

        height=500,

        showlegend=False,

        top_margin=92,
    )


# ============================================================
# QA COMPONENT PROFILE
# ============================================================

def fig_quality_components(
    quality: pd.DataFrame,
    title="QA Component Profile",
):

    required = [
        "Metric",
        "Average",
    ]


    if not _has_columns(
        quality,
        required,
    ):

        return _empty_figure(

            title,

            (
                "No numeric QA component scores "
                "are available in this view."
            ),
        )


    work = (
        quality.copy()
    )


    work["Average"] = (
        _safe_numeric(
            work[
                "Average"
            ]
        )
    )


    colors = [

        BLUE,

        PURPLE,

        CYAN,

        GREEN,

        AMBER,

        "#14B8A6",
    ]


    bar_colors = [

        colors[
            index
            % len(colors)
        ]

        for index
        in range(
            len(work)
        )
    ]


    fig = go.Figure(

        go.Bar(

            x=work[
                "Metric"
            ],

            y=work[
                "Average"
            ],

            marker=dict(
                color=bar_colors,
            ),

            text=[

                f"{value:.2f}"

                for value
                in work[
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

        height=460,

        showlegend=False,

        top_margin=92,
    )


# ============================================================
# COLLECTION INTENSITY HEATMAP
# ============================================================

def fig_calendar_heatmap(
    calendar_data: pd.DataFrame,
):

    required = [

        "Weekday",

        "Month",

        "Records",
    ]


    if not _has_columns(
        calendar_data,
        required,
    ):

        return _empty_figure(
            "Collection Intensity Heatmap"
        )


    work = (
        calendar_data.copy()
    )


    work["Records"] = (
        _safe_numeric(
            work[
                "Records"
            ]
        )
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

            x=pivot.columns.tolist(),

            y=pivot.index.tolist(),

            text=pivot.values,

            texttemplate=(
                "%{text}"
            ),

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

                title=dict(

                    text="Records",

                    font=dict(
                        color=MUTED,
                        size=11,
                    ),
                ),

                tickfont=dict(
                    color=MUTED,
                    size=10,
                ),

                thickness=10,

                len=0.78,

                outlinewidth=0,
            ),

            hovertemplate=(
                "<b>%{y} • %{x}</b>"
                "<br>"
                "Records: %{z:,}"
                "<extra></extra>"
            ),

            xgap=2,

            ygap=2,
        )
    )


    fig.update_layout(

        title=(
            "Collection Intensity Heatmap"
        ),
    )


    fig.update_xaxes(
        showgrid=False,
    )


    fig.update_yaxes(
        showgrid=False,
    )


    return _layout(

        fig,

        height=460,

        showlegend=False,

        margin=dict(
            l=85,
            r=70,
            t=92,
            b=35,
        ),
    )

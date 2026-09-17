from __future__ import annotations

from pathlib import Path
from html import escape

import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

def _get_project_root() -> Path:
    """
    Return the root directory of the Streamlit project.

    Expected structure:

    project/
    ├── app.py
    ├── assets/
    │   └── app.css
    └── src/
        └── ui.py
    """

    return (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )


# ============================================================
# FIND EXTERNAL CSS
# ============================================================

def _find_css_file() -> Path | None:
    """
    Search for assets/app.css in several safe locations.

    The application should never crash if the CSS file
    is accidentally missing or Streamlit Cloud uses a
    different working directory.
    """

    project_root = (
        _get_project_root()
    )


    possible_paths = [

        # Standard project structure
        project_root
        / "assets"
        / "app.css",

        # Fallback if assets was placed under src
        project_root
        / "src"
        / "assets"
        / "app.css",

        # Current working directory
        Path.cwd()
        / "assets"
        / "app.css",

        # Relative fallback
        Path("assets")
        / "app.css",
    ]


    for css_path in possible_paths:

        try:

            if (
                css_path.exists()
                and css_path.is_file()
            ):

                return css_path

        except (
            OSError,
            PermissionError,
        ):

            continue


    return None


# ============================================================
# MINIMAL FALLBACK CSS
# ============================================================

FALLBACK_CSS = """
:root {
    --bg-main: #07111F;
    --bg-secondary: #0B192B;
    --panel: #0E1E33;
    --border: rgba(148,163,184,0.15);
    --text-main: #E8F0FB;
    --text-muted: #8EA0B8;

    --blue: #3B82F6;
    --cyan: #22D3EE;
    --green: #22C55E;
    --red: #EF4444;
    --amber: #F59E0B;
    --purple: #8B5CF6;
}


.stApp {

    background:
        linear-gradient(
            180deg,
            #07111F 0%,
            #08111E 48%,
            #06101C 100%
        );

    color:
        var(--text-main);
}


.block-container {

    max-width:
        1760px;

    padding-top:
        1rem;

    padding-bottom:
        3rem;

    padding-left:
        1.4rem;

    padding-right:
        1.4rem;
}


/* =========================================================
   HERO
   ========================================================= */

.hero-shell {

    position:
        relative;

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    gap:
        2rem;

    overflow:
        hidden;

    padding:
        1.55rem
        1.65rem;

    margin-bottom:
        1rem;

    border:
        1px solid
        rgba(
            96,
            165,
            250,
            0.22
        );

    border-radius:
        26px;

    background:
        linear-gradient(
            135deg,
            rgba(
                18,
                39,
                67,
                0.97
            ),
            rgba(
                8,
                24,
                42,
                0.96
            )
        );

    box-shadow:
        0
        24px
        65px
        rgba(
            0,
            0,
            0,
            0.22
        );
}


.hero-kicker {

    display:
        inline-flex;

    padding:
        0.38rem
        0.7rem;

    border-radius:
        999px;

    font-size:
        0.70rem;

    font-weight:
        800;

    letter-spacing:
        0.09em;

    color:
        #8BE9FD;

    background:
        rgba(
            14,
            165,
            233,
            0.09
        );

    border:
        1px solid
        rgba(
            125,
            211,
            252,
            0.18
        );
}


.hero-title {

    margin-top:
        0.6rem;

    color:
        #FFFFFF;

    font-size:
        clamp(
            1.8rem,
            3vw,
            2.7rem
        );

    font-weight:
        800;

    line-height:
        1.06;

    letter-spacing:
        -0.05em;
}


.hero-subtitle {

    margin-top:
        0.55rem;

    max-width:
        1050px;

    color:
        #AABBD0;

    font-size:
        0.96rem;

    line-height:
        1.6;
}


.hero-orb {

    display:
        grid;

    place-items:
        center;

    min-width:
        78px;

    min-height:
        78px;

    border-radius:
        26px;

    color:
        #67E8F9;

    font-size:
        2rem;

    background:
        linear-gradient(
            145deg,
            rgba(
                59,
                130,
                246,
                0.24
            ),
            rgba(
                34,
                211,
                238,
                0.08
            )
        );

    border:
        1px solid
        rgba(
            103,
            232,
            249,
            0.18
        );
}


/* =========================================================
   KPI CARDS
   ========================================================= */

.metric-shell {

    position:
        relative;

    overflow:
        hidden;

    min-height:
        128px;

    padding:
        1rem;

    margin-bottom:
        0.72rem;

    border:
        1px solid
        var(--border);

    border-radius:
        20px;

    background:
        linear-gradient(
            180deg,
            rgba(
                14,
                30,
                51,
                0.96
            ),
            rgba(
                9,
                21,
                37,
                0.96
            )
        );

    box-shadow:
        0
        14px
        34px
        rgba(
            0,
            0,
            0,
            0.14
        );
}


.metric-shell::before {

    content:
        "";

    position:
        absolute;

    left:
        0;

    top:
        18%;

    width:
        3px;

    height:
        64%;

    border-radius:
        999px;

    background:
        #64748B;
}


.tone-blue::before {
    background:
        var(--blue);
}


.tone-green::before {
    background:
        var(--green);
}


.tone-red::before {
    background:
        var(--red);
}


.tone-amber::before {
    background:
        var(--amber);
}


.tone-purple::before {
    background:
        var(--purple);
}


.tone-cyan::before {
    background:
        var(--cyan);
}


.metric-label {

    color:
        #8EA0B8;

    font-size:
        0.69rem;

    font-weight:
        800;

    letter-spacing:
        0.075em;

    text-transform:
        uppercase;
}


.metric-value {

    margin-top:
        0.34rem;

    color:
        #F8FBFF;

    font-size:
        clamp(
            1.45rem,
            2.3vw,
            2.1rem
        );

    font-weight:
        800;

    line-height:
        1.03;

    letter-spacing:
        -0.035em;
}


.metric-note {

    margin-top:
        0.5rem;

    color:
        #7F93AD;

    font-size:
        0.73rem;

    line-height:
        1.42;
}


/* =========================================================
   SECTION HEADINGS
   ========================================================= */

.section-shell {

    margin:
        1.2rem
        0
        0.7rem;
}


.section-title {

    color:
        #F3F8FF;

    font-size:
        1.1rem;

    font-weight:
        800;

    letter-spacing:
        -0.018em;
}


.section-subtitle {

    margin-top:
        0.16rem;

    color:
        #7F93AD;

    font-size:
        0.79rem;
}


/* =========================================================
   PANEL TITLE
   ========================================================= */

.panel-title-shell {

    margin:
        0.35rem
        0
        0.75rem;
}


.panel-title {

    color:
        #EAF2FF;

    font-size:
        0.94rem;

    font-weight:
        800;
}


.panel-subtitle {

    margin-top:
        0.15rem;

    color:
        #7186A3;

    font-size:
        0.75rem;
}


/* =========================================================
   INSIGHT CARDS
   ========================================================= */

.insight-card {

    min-height:
        140px;

    padding:
        1rem;

    margin-bottom:
        0.65rem;

    border-radius:
        19px;

    border:
        1px solid
        var(--border);

    background:
        linear-gradient(
            180deg,
            rgba(
                11,
                25,
                43,
                0.92
            ),
            rgba(
                8,
                20,
                34,
                0.92
            )
        );

    box-shadow:
        0
        10px
        26px
        rgba(
            0,
            0,
            0,
            0.12
        );
}


.insight-title {

    font-size:
        0.75rem;

    font-weight:
        800;

    letter-spacing:
        0.07em;

    text-transform:
        uppercase;
}


.insight-text {

    margin-top:
        0.52rem;

    color:
        #C5D3E4;

    font-size:
        0.86rem;

    line-height:
        1.62;
}


.insight-critical {

    border-color:
        rgba(
            239,
            68,
            68,
            0.30
        );
}


.insight-critical
.insight-title {

    color:
        #F87171;
}


.insight-warning {

    border-color:
        rgba(
            245,
            158,
            11,
            0.28
        );
}


.insight-warning
.insight-title {

    color:
        #FBBF24;
}


.insight-positive {

    border-color:
        rgba(
            34,
            197,
            94,
            0.28
        );
}


.insight-positive
.insight-title {

    color:
        #4ADE80;
}


.insight-neutral
.insight-title {

    color:
        #7DD3FC;
}


/* =========================================================
   CONTEXT PILLS
   ========================================================= */

.context-strip {

    display:
        flex;

    flex-wrap:
        wrap;

    align-items:
        center;

    gap:
        0.55rem;

    margin:
        0.3rem
        0
        1.05rem;
}


.context-pill {

    display:
        inline-flex;

    align-items:
        center;

    white-space:
        nowrap;

    padding:
        0.38rem
        0.72rem;

    border-radius:
        999px;

    background:
        rgba(
            15,
            23,
            42,
            0.72
        );

    border:
        1px solid
        rgba(
            148,
            163,
            184,
            0.14
        );

    color:
        #B5C4D7;

    font-size:
        0.75rem;

    font-weight:
        600;
}


/* =========================================================
   EMPTY STATE
   ========================================================= */

.empty-state {

    padding:
        3rem
        1rem;

    text-align:
        center;

    border:
        1px dashed
        rgba(
            148,
            163,
            184,
            0.22
        );

    border-radius:
        22px;

    background:
        rgba(
            15,
            23,
            42,
            0.42
        );
}


.empty-title {

    color:
        #DBEAFE;

    font-size:
        1.05rem;

    font-weight:
        800;
}


.empty-text {

    margin-top:
        0.4rem;

    color:
        #7F93AD;
}


/* =========================================================
   DIVIDER
   ========================================================= */

.lux-divider {

    height:
        1px;

    margin:
        1.2rem
        0;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(
                96,
                165,
                250,
                0.22
            ),
            transparent
        );
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer-shell {

    display:
        flex;

    justify-content:
        space-between;

    flex-wrap:
        wrap;

    gap:
        1rem;

    margin-top:
        2rem;

    padding-top:
        1rem;

    border-top:
        1px solid
        var(--border);

    color:
        #60748F;

    font-size:
        0.71rem;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (
    max-width: 1200px
) {

    .block-container {

        padding-left:
            1rem;

        padding-right:
            1rem;
    }


    .metric-shell {

        min-height:
            112px;

        padding:
            0.86rem;
    }


    .metric-value {

        font-size:
            1.52rem;
    }

}


@media (
    max-width: 760px
) {

    .block-container {

        padding-left:
            0.7rem;

        padding-right:
            0.7rem;
    }


    .hero-orb {

        display:
            none;
    }


    .hero-title {

        font-size:
            1.68rem;
    }


    .hero-subtitle {

        font-size:
            0.86rem;
    }


    .metric-shell {

        min-height:
            auto;
    }

}
"""


# ============================================================
# EXTERNAL CSS INJECTION
# ============================================================

def inject_css() -> None:
    """
    Load assets/app.css safely.

    If app.css does not exist or cannot be read,
    use FALLBACK_CSS instead of crashing the app.
    """

    css_path = (
        _find_css_file()
    )


    css_content = None


    if css_path is not None:

        try:

            css_content = (
                css_path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            FileNotFoundError,
            PermissionError,
            UnicodeDecodeError,
            OSError,
        ):

            css_content = None


    if not css_content:

        css_content = (
            FALLBACK_CSS
        )


    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True,
    )


# ============================================================
# DARK MODE + SIDEBAR CONTROL PROTECTION
# ============================================================

def force_dark_mode() -> None:
    """
    Force the Streamlit dashboard to remain visually dark while
    preserving the native sidebar open / close controls.

    IMPORTANT:
    - Do NOT hide stHeader.
    - Do NOT hide stToolbar.
    - Do NOT hide sidebar collapse controls.
    """

    st.markdown(
        """
        <style>

        /* =====================================================
           GLOBAL DARK COLOR SCHEME
           ===================================================== */

        :root {

            color-scheme:
                dark !important;
        }


        html {

            color-scheme:
                dark !important;

            background-color:
                #07111F !important;
        }


        body {

            color-scheme:
                dark !important;

            background-color:
                #07111F !important;

            color:
                #E8F0FB !important;
        }


        /* =====================================================
           MAIN APP
           ===================================================== */

        .stApp,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {

            background:
                linear-gradient(
                    180deg,
                    #07111F 0%,
                    #08111E 48%,
                    #06101C 100%
                ) !important;

            color:
                #E8F0FB !important;
        }


        /* =====================================================
           STREAMLIT HEADER
           =====================================================
           
           Keep the header visible because Streamlit may place
           sidebar controls inside this region.
           ===================================================== */

        [data-testid="stHeader"] {

            display:
                block !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

            background:
                rgba(
                    7,
                    17,
                    31,
                    0.94
                ) !important;

            backdrop-filter:
                blur(12px);

            border-bottom:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.06
                );
        }


        /* =====================================================
           TOOLBAR
           =====================================================
           
           DO NOT set display:none.
           This is intentional.
           ===================================================== */

        [data-testid="stToolbar"] {

            display:
                flex !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

            background:
                transparent !important;
        }


        /* =====================================================
           SIDEBAR
           ===================================================== */

        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] {

            background:
                linear-gradient(
                    180deg,
                    #081421 0%,
                    #07111F 100%
                ) !important;

            color:
                #E8F0FB !important;

            border-right:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.14
                ) !important;

            box-shadow:
                14px
                0
                40px
                rgba(
                    0,
                    0,
                    0,
                    0.14
                );
        }


        [data-testid="stSidebarContent"] {

            background:
                transparent !important;
        }


        [data-testid="stSidebar"] * {

            color:
                #E8F0FB;
        }


        /* =====================================================
           SIDEBAR COLLAPSE BUTTON
           ===================================================== */

        [data-testid="stSidebarCollapseButton"] {

            display:
                flex !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

            pointer-events:
                auto !important;

            z-index:
                999999 !important;
        }


        [data-testid="stSidebarCollapseButton"]
        button {

            display:
                flex !important;

            align-items:
                center !important;

            justify-content:
                center !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

            pointer-events:
                auto !important;

            color:
                #E8F0FB !important;

            background:
                rgba(
                    16,
                    34,
                    58,
                    0.88
                ) !important;

            border:
                1px solid
                rgba(
                    148,
                    163,
                    184,
                    0.16
                ) !important;

            border-radius:
                10px !important;
        }


        [data-testid="stSidebarCollapseButton"]
        button:hover {

            background:
                #102A48 !important;

            border-color:
                rgba(
                    34,
                    211,
                    238,
                    0.35
                ) !important;
        }


        /* =====================================================
           COLLAPSED SIDEBAR OPEN CONTROL
           ===================================================== */

        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {

            display:
                flex !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

            pointer-events:
                auto !important;

            z-index:
                999999 !important;
        }


        [data-testid="stSidebarCollapsedControl"]
        button,

        [data-testid="collapsedControl"]
        button {

            display:
                flex !important;

            align-items:
                center !important;

            justify-content:
                center !important;

            visibility:
                visible !important;

            opacity:
                1 !important;

            pointer-events:
                auto !important;

            width:
                40px !important;

            height:
                40px !important;

            border-radius:
                11px !important;

            color:
                #E8F0FB !important;

            background:
                rgba(
                    11,
                    25,
                    43,
                    0.96
                ) !important;

            border:
                1px solid
                rgba(
                    96,
                    165,
                    250,
                    0.22
                ) !important;

            box-shadow:
                0
                8px
                20px
                rgba(
                    0,
                    0,
                    0,
                    0.20
                ) !important;
        }


        [data-testid="stSidebarCollapsedControl"]
        button:hover,

        [data-testid="collapsedControl"]
        button:hover {

            background:
                #102A48 !important;

            border-color:
                rgba(
                    34,
                    211,
                    238,
                    0.40
                ) !important;
        }


        /* =====================================================
           SIDEBAR CONTROL ICONS
           ===================================================== */

        [data-testid="stSidebarCollapseButton"]
        svg,

        [data-testid="stSidebarCollapsedControl"]
        svg,

        [data-testid="collapsedControl"]
        svg {

            color:
                #CBD5E1 !important;

            fill:
                #CBD5E1 !important;

            opacity:
                1 !important;
        }


        /* =====================================================
           HIDE ONLY MAIN MENU
           =====================================================
           
           We hide the three-dot menu, NOT the whole toolbar.
           ===================================================== */

        #MainMenu,
        [data-testid="stMainMenu"],
        button[aria-label="Main menu"] {

            display:
                none !important;

            visibility:
                hidden !important;
        }


        /* =====================================================
           DECORATION
           ===================================================== */

        [data-testid="stDecoration"] {

            display:
                none !important;
        }


        /* =====================================================
           SELECT / MULTISELECT / INPUT
           ===================================================== */

        input,
        textarea,
        select {

            color-scheme:
                dark !important;

            background-color:
                #0B192B !important;

            color:
                #E8F0FB !important;

            border-color:
                #1E334D !important;
        }


        input::placeholder,
        textarea::placeholder {

            color:
                #64748B !important;
        }


        [data-baseweb="select"] > div,
        [data-baseweb="input"],
        [data-baseweb="textarea"],
        [data-baseweb="base-input"] {

            background-color:
                #0B192B !important;

            color:
                #E8F0FB !important;

            border-color:
                #1E334D !important;
        }


        /* =====================================================
           DROPDOWN MENU
           ===================================================== */

        [role="listbox"],
        [role="option"],
        [data-baseweb="menu"] {

            background-color:
                #0B192B !important;

            color:
                #E8F0FB !important;
        }


        [role="option"]:hover {

            background-color:
                #102A48 !important;
        }


        /* =====================================================
           POPOVER
           ===================================================== */

        [data-baseweb="popover"],
        [data-baseweb="popover"] > div {

            background-color:
                #0B192B !important;

            color:
                #E8F0FB !important;
        }


        /* =====================================================
           TABS
           ===================================================== */

        [data-baseweb="tab-list"] {

            background-color:
                rgba(
                    8,
                    20,
                    35,
                    0.90
                ) !important;
        }


        /* =====================================================
           EXPANDER
           ===================================================== */

        [data-testid="stExpander"] {

            background-color:
                #0B192B !important;

            border-color:
                #1E334D !important;
        }


        /* =====================================================
           DATAFRAME
           ===================================================== */

        [data-testid="stDataFrame"] {

            background-color:
                #0B192B !important;
        }


        /* =====================================================
           FORM
           ===================================================== */

        [data-testid="stForm"] {

            background-color:
                rgba(
                    11,
                    25,
                    43,
                    0.72
                ) !important;

            border-color:
                #1E334D !important;
        }


        /* =====================================================
           DOWNLOAD BUTTON / STANDARD BUTTONS
           ===================================================== */

        button {

            transition:
                all
                0.18s
                ease !important;
        }


        /* =====================================================
           SCROLLBAR
           ===================================================== */

        ::-webkit-scrollbar {

            width:
                10px;

            height:
                10px;
        }


        ::-webkit-scrollbar-track {

            background:
                #07111F;
        }


        ::-webkit-scrollbar-thumb {

            background:
                #263A54;

            border-radius:
                10px;
        }


        ::-webkit-scrollbar-thumb:hover {

            background:
                #36516F;
        }


        /* =====================================================
           MOBILE
           ===================================================== */

        @media (
            max-width: 760px
        ) {

            [data-testid="stSidebarCollapsedControl"],
            [data-testid="collapsedControl"] {

                position:
                    fixed !important;

                top:
                    0.55rem !important;

                left:
                    0.55rem !important;

                z-index:
                    999999 !important;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

def hero(
    title: str,
    subtitle: str,
    badge: str = "LIVE DASHBOARD",
) -> None:
    """
    Render the main dashboard hero area.
    """

    safe_title = (
        escape(
            str(title)
        )
    )


    safe_subtitle = (
        escape(
            str(subtitle)
        )
    )


    safe_badge = (
        escape(
            str(badge)
        )
    )


    st.html(
        f"""
        <div class="hero-shell">

            <div>

                <div class="hero-kicker">
                    {safe_badge}
                </div>

                <div class="hero-title">
                    {safe_title}
                </div>

                <div class="hero-subtitle">
                    {safe_subtitle}
                </div>

            </div>

            <div class="hero-orb">
                ◈
            </div>

        </div>
        """
    )


# ============================================================
# KPI METRIC CARD
# ============================================================

def metric_card(
    label: str,
    value: str,
    note: str = "",
    tone: str = "neutral",
) -> None:
    """
    Render a premium dashboard KPI card.
    """

    valid_tones = {

        "neutral",

        "blue",

        "green",

        "red",

        "amber",

        "purple",

        "cyan",
    }


    if tone not in valid_tones:

        tone = "neutral"


    safe_label = (
        escape(
            str(label)
        )
    )


    safe_value = (
        escape(
            str(value)
        )
    )


    safe_note = (
        escape(
            str(note)
        )
    )


    st.html(
        f"""
        <div class="metric-shell tone-{tone}">

            <div class="metric-label">
                {safe_label}
            </div>

            <div class="metric-value">
                {safe_value}
            </div>

            <div class="metric-note">
                {safe_note}
            </div>

        </div>
        """
    )


# ============================================================
# SECTION HEADER
# ============================================================

def section_header(
    title: str,
    subtitle: str = "",
) -> None:
    """
    Render a dashboard section heading.
    """

    safe_title = (
        escape(
            str(title)
        )
    )


    safe_subtitle = (
        escape(
            str(subtitle)
        )
    )


    st.html(
        f"""
        <div class="section-shell">

            <div class="section-title">
                {safe_title}
            </div>

            <div class="section-subtitle">
                {safe_subtitle}
            </div>

        </div>
        """
    )


# ============================================================
# PANEL TITLE
# ============================================================

def panel_title(
    title: str,
    subtitle: str = "",
) -> None:
    """
    Render a smaller panel heading.
    """

    safe_title = (
        escape(
            str(title)
        )
    )


    safe_subtitle = (
        escape(
            str(subtitle)
        )
    )


    st.html(
        f"""
        <div class="panel-title-shell">

            <div class="panel-title">
                {safe_title}
            </div>

            <div class="panel-subtitle">
                {safe_subtitle}
            </div>

        </div>
        """
    )


# ============================================================
# INSIGHT CARD
# ============================================================

def insight_card(
    title: str,
    text: str,
    level: str = "neutral",
) -> None:
    """
    Render a management insight card.
    """

    valid_levels = {

        "neutral",

        "positive",

        "warning",

        "critical",
    }


    if level not in valid_levels:

        level = "neutral"


    safe_title = (
        escape(
            str(title)
        )
    )


    safe_text = (
        escape(
            str(text)
        )
    )


    st.html(
        f"""
        <div class="insight-card insight-{level}">

            <div class="insight-title">
                {safe_title}
            </div>

            <div class="insight-text">
                {safe_text}
            </div>

        </div>
        """
    )


# ============================================================
# CONTEXT PILL
# ============================================================

def pill(
    text: str,
) -> str:
    """
    Return a small HTML context badge.

    app.py renders these using st.html().
    """

    safe_text = (
        escape(
            str(text)
        )
    )


    return (
        '<span class="context-pill">'
        f'{safe_text}'
        '</span>'
    )


# ============================================================
# EMPTY STATE
# ============================================================

def show_empty_state(
    title: str,
    text: str,
) -> None:
    """
    Render a safe empty-state message.
    """

    safe_title = (
        escape(
            str(title)
        )
    )


    safe_text = (
        escape(
            str(text)
        )
    )


    st.html(
        f"""
        <div class="empty-state">

            <div class="empty-title">
                {safe_title}
            </div>

            <div class="empty-text">
                {safe_text}
            </div>

        </div>
        """
    )


# ============================================================
# DIVIDER
# ============================================================

def divider() -> None:
    """
    Render a subtle dashboard divider.
    """

    st.html(
        '<div class="lux-divider"></div>'
    )


# ============================================================
# FOOTER
# ============================================================

def footer(
    source: str,
    spreadsheet_id: str,
) -> None:
    """
    Render the dashboard footer.
    """

    safe_source = (
        escape(
            str(source)
        )
    )


    safe_spreadsheet_id = (
        escape(
            str(spreadsheet_id)
        )
    )


    st.html(
        f"""
        <div class="footer-shell">

            <span>
                {safe_source}
            </span>

            <span>
                Spreadsheet ID:
                {safe_spreadsheet_id}
            </span>

        </div>
        """
    )

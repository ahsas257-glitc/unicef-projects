from __future__ import annotations
from pathlib import Path
import streamlit as st


def _find_css_file() -> Path | None:
    root = Path(__file__).resolve().parent.parent
    for p in [root / "assets" / "app.css", Path.cwd() / "assets" / "app.css", Path("assets/app.css")]:
        try:
            if p.exists() and p.is_file():
                return p
        except Exception:
            pass
    return None


def inject_css() -> None:
    css_file = _find_css_file()
    if css_file:
        try:
            st.markdown(f"<style>{css_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
        except Exception:
            pass


def force_dark_mode() -> None:
    st.markdown("""
    <style>
    :root{color-scheme:dark!important}html,body,.stApp,[data-testid="stAppViewContainer"]{background:#07111F!important;color:#E8F0FB!important}
    [data-testid="stHeader"]{background:rgba(7,17,31,.96)!important}
    [data-testid="stSidebar"],[data-testid="stSidebarContent"]{background:linear-gradient(180deg,#081421 0%,#07111F 100%)!important;color:#E8F0FB!important}
    #MainMenu,[data-testid="stToolbar"],[data-testid="stToolbarActions"],[data-testid="stMainMenu"],button[aria-label="Main menu"],[data-testid="stDecoration"]{visibility:hidden!important;display:none!important}
    input,textarea,select{color-scheme:dark!important}
    </style>
    """, unsafe_allow_html=True)


def hero(title, subtitle, badge):
    st.markdown(f'<div class="hero-shell"><div><div class="hero-kicker">{badge}</div><div class="hero-title">{title}</div><div class="hero-subtitle">{subtitle}</div></div><div class="hero-orb">◈</div></div>', unsafe_allow_html=True)


def metric_card(label, value, note, tone="neutral"):
    st.markdown(f'<div class="metric-shell tone-{tone}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)


def section_header(title, subtitle=""):
    st.markdown(f'<div class="section-shell"><div class="section-title">{title}</div><div class="section-subtitle">{subtitle}</div></div>', unsafe_allow_html=True)


def panel_title(title, subtitle=""):
    st.markdown(f'<div class="panel-title-shell"><div class="panel-title">{title}</div><div class="panel-subtitle">{subtitle}</div></div>', unsafe_allow_html=True)


def insight_card(title, text, level="neutral"):
    st.markdown(f'<div class="insight-card insight-{level}"><div class="insight-title">{title}</div><div class="insight-text">{text}</div></div>', unsafe_allow_html=True)


def pill(text):
    return f'<span class="context-pill">{text}</span>'


def show_empty_state(title, text):
    st.markdown(f'<div class="empty-state"><div class="empty-title">{title}</div><div class="empty-text">{text}</div></div>', unsafe_allow_html=True)


def footer(source, spreadsheet_id):
    st.markdown(f'<div class="footer-shell"><span>{source}</span><span>Spreadsheet ID: {spreadsheet_id}</span></div>', unsafe_allow_html=True)

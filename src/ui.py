from __future__ import annotations

from pathlib import Path

import streamlit as st

def inject_css():
    css_path = Path(__file__).resolve().parents[1] / "assets" / "app.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def hero(title, subtitle, badge):
    st.markdown(
        f"""
        <div class="hero-shell">
          <div>
            <div class="hero-kicker">{badge}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
          </div>
          <div class="hero-orb">◈</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def metric_card(label, value, note, tone="neutral"):
    st.markdown(
        f"""
        <div class="metric-shell tone-{tone}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-shell">
          <div class="section-title">{title}</div>
          <div class="section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def insight_card(title, text, level="neutral"):
    st.markdown(
        f"""
        <div class="insight-card insight-{level}">
          <div class="insight-title">{title}</div>
          <div class="insight-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def pill(text):
    return f'<span class="context-pill">{text}</span>'

def show_empty_state(title, text):
    st.markdown(
        f"""
        <div class="empty-state">
          <div class="empty-title">{title}</div>
          <div class="empty-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def footer(source, spreadsheet_id):
    st.markdown(
        f"""
        <div class="footer-shell">
          <span>{source}</span>
          <span>Spreadsheet ID: {spreadsheet_id}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

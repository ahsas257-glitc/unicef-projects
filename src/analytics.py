from __future__ import annotations

import math
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

def apply_filters(df, provinces=None, statuses=None, tools=None, search_text=""):
    out = df.copy()

    if provinces:
        out = out[out["province"].isin(provinces)]
    if statuses:
        out = out[out["status"].isin(statuses)]
    if tools:
        out = out[out["tool_type"].isin(tools)]
    if search_text:
        cols = ["project", "subsource", "province", "district", "tool_type", "status", "rejection_reason", "phase", "discipline", "gender"]
        cols = [c for c in cols if c in out.columns]
        text = out[cols].fillna("").astype(str).agg(" | ".join, axis=1)
        out = out[text.str.contains(search_text, case=False, regex=False)]
    return out

def _health(completion, rejection_rate, backlog_rate):
    if completion >= 1:
        return "Scope Reached", "Maintain quality"
    if rejection_rate >= 0.30 or backlog_rate >= 0.20:
        return "High Risk", "Resolve QA and rejection drivers"
    if completion < 0.25:
        return "Low Progress", "Accelerate completion"
    if completion < 0.50:
        return "Watch", "Increase throughput"
    return "Stable", "Monitor"

def project_summary(df, project, scope):
    received = len(df)
    approved = int(df["is_approved"].sum()) if received else 0
    rejected = int(df["is_rejected"].sum()) if received else 0
    pending = int(df["is_pending"].sum()) if received else 0

    completion = min(approved / scope, 1) if scope else 0
    coverage = received / scope if scope else 0
    approval_rate = approved / received if received else 0
    rejection_rate = rejected / received if received else 0
    reviewed = (approved + rejected) / received if received else 0
    backlog = pending / received if received else 0
    remaining = max(scope - approved, 0)

    health, action = _health(completion, rejection_rate, backlog)

    return {
        "Project": project,
        "Scope": scope,
        "Received": received,
        "Approved": approved,
        "Rejected": rejected,
        "Pending / Unreviewed": pending,
        "Remaining": remaining,
        "Completion %": completion,
        "Collection Coverage %": coverage,
        "Approval Rate %": approval_rate,
        "Rejection Rate %": rejection_rate,
        "QC Reviewed %": reviewed,
        "Backlog %": backlog,
        "Health Flag": health,
        "Priority Action": action,
    }

def portfolio_summary(df, scopes, projects, honor_input_as_filtered=False):
    rows = []
    for project in projects:
        part = df[df["project"].eq(project)].copy()
        rows.append(project_summary(part, project, scopes.get(project, 0)))
    return pd.DataFrame(rows)

def monthly_summary(df, year):
    months = pd.date_range(f"{year}-01-01", f"{year}-12-01", freq="MS")
    dated = df[df["date"].notna()].copy()

    rows = []
    for month in months:
        next_month = month + pd.offsets.MonthBegin(1)
        part = dated[(dated["date"] >= month) & (dated["date"] < next_month)]
        received = len(part)
        approved = int(part["is_approved"].sum())
        rejected = int(part["is_rejected"].sum())
        pending = int(part["is_pending"].sum())
        rows.append({
            "Month": month,
            "Received": received,
            "Approved": approved,
            "Rejected": rejected,
            "Pending": pending,
            "Approval Rate": approved / received if received else 0,
        })
    return pd.DataFrame(rows)

def province_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["Province", "Received", "Approved", "Rejected", "Pending", "Approval Rate %", "Rejection Rate %", "Backlog %"])

    work = df.copy()
    work["province"] = work["province"].replace("", "Unknown").fillna("Unknown")

    out = (
        work.groupby("province", dropna=False)
        .agg(
            Received=("project", "size"),
            Approved=("is_approved", "sum"),
            Rejected=("is_rejected", "sum"),
            Pending=("is_pending", "sum"),
        )
        .reset_index()
        .rename(columns={"province": "Province"})
    )
    out["Approval Rate %"] = np.where(out["Received"] > 0, out["Approved"] / out["Received"], 0)
    out["Rejection Rate %"] = np.where(out["Received"] > 0, out["Rejected"] / out["Received"], 0)
    out["Backlog %"] = np.where(out["Received"] > 0, out["Pending"] / out["Received"], 0)
    return out.sort_values(["Received", "Approval Rate %"], ascending=[False, False])

def rejection_summary(df, top_n=15):
    rejected = df[df["is_rejected"]].copy()
    if rejected.empty:
        return pd.DataFrame(columns=["Reason", "Count", "Cumulative %"])

    rejected["Reason"] = rejected["rejection_reason"].replace("", "No reason documented").fillna("No reason documented")
    out = (
        rejected.groupby("Reason")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
        .head(top_n)
    )
    total = out["Count"].sum()
    out["Cumulative %"] = out["Count"].cumsum() / total if total else 0
    return out

def staff_summary(df, top_n=30):
    if df.empty:
        return pd.DataFrame(columns=["Field Staff", "Received", "Approved", "Rejected", "Pending", "Approval Rate %", "Rejection Rate %"])

    out = (
        df.groupby("staff_alias")
        .agg(
            Received=("project", "size"),
            Approved=("is_approved", "sum"),
            Rejected=("is_rejected", "sum"),
            Pending=("is_pending", "sum"),
        )
        .reset_index()
        .rename(columns={"staff_alias": "Field Staff"})
    )
    out["Approval Rate %"] = np.where(out["Received"] > 0, out["Approved"] / out["Received"], 0)
    out["Rejection Rate %"] = np.where(out["Received"] > 0, out["Rejected"] / out["Received"], 0)
    return out.sort_values("Received", ascending=False).head(top_n)

def quality_summary(df):
    metrics = {
        "Background Audit": "background_audit",
        "Photo Quality": "photo_quality",
        "Audio Quality": "audio_quality",
        "Form Accuracy": "form_accuracy",
        "Form / Enumerator Rating": "form_rating",
    }
    rows = []
    for label, col in metrics.items():
        if col not in df.columns:
            continue
        vals = pd.to_numeric(df[col], errors="coerce").dropna()
        if not vals.empty:
            rows.append({
                "Metric": label,
                "Average": float(vals.mean()),
                "Records Scored": int(vals.count()),
            })
    return pd.DataFrame(rows)

def vt_tool_summary(df):
    vt = df[df["project"].eq("VT")].copy()
    if vt.empty:
        return pd.DataFrame(columns=["VT Tool Type", "Received", "Approved", "Rejected", "Pending", "Approval Rate %", "Rejection Rate %", "QC Reviewed %", "Backlog %"])

    out = (
        vt.groupby("tool_type")
        .agg(
            Received=("project", "size"),
            Approved=("is_approved", "sum"),
            Rejected=("is_rejected", "sum"),
            Pending=("is_pending", "sum"),
        )
        .reset_index()
        .rename(columns={"tool_type": "VT Tool Type"})
    )
    out["Approval Rate %"] = np.where(out["Received"] > 0, out["Approved"] / out["Received"], 0)
    out["Rejection Rate %"] = np.where(out["Received"] > 0, out["Rejected"] / out["Received"], 0)
    out["QC Reviewed %"] = np.where(out["Received"] > 0, (out["Approved"] + out["Rejected"]) / out["Received"], 0)
    out["Backlog %"] = np.where(out["Received"] > 0, out["Pending"] / out["Received"], 0)
    return out.sort_values("Received", ascending=False)

def data_quality_summary(df, year):
    now = pd.Timestamp.now(tz=ZoneInfo("Asia/Kabul")).tz_localize(None).normalize()
    future = int((df["date"].notna() & (df["date"] > now)).sum())
    undated_kii = int((df["project"].eq("VT") & df["subsource"].eq("VT KII/FGD") & df["date"].isna()).sum())
    missing_reason = int((df["is_rejected"] & df["rejection_reason"].fillna("").str.strip().eq("")).sum())
    return {
        "future_dated": future,
        "undated_vt_kii_fgd": undated_kii,
        "rejected_missing_reason": missing_reason,
    }

def executive_insights(summary, df, year):
    insights = []

    if summary.empty:
        return [{"title": "No data", "text": "No portfolio records are available for the current selection.", "level": "neutral"}]

    low = summary.sort_values("Completion %").iloc[0]
    high_rej = summary.sort_values("Rejection Rate %", ascending=False).iloc[0]
    high_backlog = summary.sort_values("Backlog %", ascending=False).iloc[0]

    insights.append({
        "title": "Delivery pressure",
        "text": f"{low['Project']} has the lowest completion at {low['Completion %']:.1%}, with {int(low['Remaining']):,} approvals still required against scope.",
        "level": "warning" if low["Completion %"] < .5 else "positive",
    })

    insights.append({
        "title": "Quality risk",
        "text": f"{high_rej['Project']} currently has the highest rejection rate at {high_rej['Rejection Rate %']:.1%}.",
        "level": "critical" if high_rej["Rejection Rate %"] >= .25 else "warning",
    })

    insights.append({
        "title": "QA backlog",
        "text": f"{high_backlog['Project']} has the largest pending share at {high_backlog['Backlog %']:.1%}.",
        "level": "warning" if high_backlog["Backlog %"] >= .10 else "positive",
    })

    return insights

def _category_counts(df, col, label):
    if col not in df.columns or df.empty:
        return pd.DataFrame(columns=[label, "Records"])
    work = df[col].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out = work.value_counts().rename_axis(label).reset_index(name="Records")
    return out.head(20)

def project_specific_breakdowns(df, project):
    out = {}
    if df.empty:
        return out

    if project == "Moraa":
        out["phase"] = _category_counts(df, "phase", "Phase")
        out["discipline"] = _category_counts(df, "discipline", "Discipline")
        out["gender"] = _category_counts(df, "gender", "Gender")
        sun = df[["phase", "discipline", "status"]].copy()
        sun.columns = ["Phase", "Discipline", "Status"]
        out["sunburst"] = sun
        return out

    out["tool"] = _category_counts(df, "tool_type", "Tool")
    out["qc_reviewer"] = _category_counts(df, "qc_alias", "QC Reviewer")
    return out


def district_summary(df):
    return _category_counts(df, "district", "District")


def qc_reviewer_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["QA Reviewer", "Reviewed", "Approved", "Rejected", "Approval Rate %"])
    work = df[df["status"].isin(["Approved", "Rejected"])].copy()
    if work.empty:
        return pd.DataFrame(columns=["QA Reviewer", "Reviewed", "Approved", "Rejected", "Approval Rate %"])
    out = (
        work.groupby("qc_alias")
        .agg(Reviewed=("project", "size"), Approved=("is_approved", "sum"), Rejected=("is_rejected", "sum"))
        .reset_index()
        .rename(columns={"qc_alias": "QA Reviewer"})
    )
    out["Approval Rate %"] = np.where(out["Reviewed"] > 0, out["Approved"] / out["Reviewed"], 0)
    return out.sort_values("Reviewed", ascending=False).head(20)


def province_quality_index(df):
    out = province_summary(df).copy()
    if out.empty:
        return out
    out["Quality Index"] = (
        0.55 * out["Approval Rate %"]
        + 0.25 * (1 - out["Rejection Rate %"])
        + 0.20 * (1 - out["Backlog %"])
    )
    return out.sort_values(["Quality Index", "Received"], ascending=[False, False])


def calendar_heatmap_data(df, year):
    work = df[df["date"].notna()].copy()
    if work.empty:
        return pd.DataFrame(columns=["Date", "Records", "Weekday", "Month"])
    out = work.groupby(work["date"].dt.normalize()).size().reset_index(name="Records")
    out.columns = ["Date", "Records"]
    out["Weekday"] = out["Date"].dt.day_name()
    out["Month"] = out["Date"].dt.strftime("%b")
    return out

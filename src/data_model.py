from __future__ import annotations

import hashlib
import re
from typing import Dict, Tuple

import numpy as np
import pandas as pd

def _norm_col(name: object) -> str:
    return re.sub(r"\s+", " ", str(name).strip()).lower()

def _get(df: pd.DataFrame, *names: str, default=None) -> pd.Series:
    mapping = {_norm_col(c): c for c in df.columns}
    for name in names:
        key = _norm_col(name)
        if key in mapping:
            return df[mapping[key]]
    return pd.Series([default] * len(df), index=df.index)

def _parse_dates(series: pd.Series) -> pd.Series:
    s = series.copy()

    # Google Sheets API returns true date cells as serial numbers.
    # Parse them explicitly before text dates so 46139 is not read as
    # nanoseconds after 1970.
    numeric = pd.to_numeric(s, errors="coerce")
    serial_mask = numeric.between(20000, 80000)
    excel_dates = pd.Timestamp("1899-12-30") + pd.to_timedelta(numeric, unit="D")
    excel_dates = excel_dates.where(serial_mask)

    text_source = s.mask(serial_mask)
    parsed = pd.to_datetime(text_source, errors="coerce", dayfirst=False)

    missing = parsed.isna() & ~serial_mask
    if missing.any():
        parsed2 = pd.to_datetime(text_source[missing], errors="coerce", dayfirst=True)
        parsed.loc[missing] = parsed2

    parsed.loc[serial_mask] = excel_dates.loc[serial_mask]
    return pd.to_datetime(parsed, errors="coerce")

def _status(value) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "Unreviewed"
    text = str(value).strip()
    if not text:
        return "Unreviewed"
    low = text.lower()

    if "approv" in low or low in {"complete", "completed"}:
        return "Approved"
    if "reject" in low:
        return "Rejected"
    if "pend" in low:
        return "Pending"
    return text.title()

def _alias(value: object, prefix: str) -> str:
    text = str(value or "").strip()
    if not text:
        return "Unknown"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:4].upper()
    return f"{prefix}-{digest}"

def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")

def _base_frame(df: pd.DataFrame, project: str, subsource: str) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["project"] = project
    out["subsource"] = subsource
    out["record_id"] = _get(df, "KEY", "Case_ID", "caseid", "Moraa_Enrolment_ID", "No")
    out["province"] = _get(df, "Province", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["district"] = _get(df, "District", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["tool_type"] = _get(df, "Tool type", "Tool Name", "Type", "Phase", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["phase"] = _get(df, "Phase", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["discipline"] = _get(df, "Decipline", "Discipline", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["gender"] = _get(df, "N_Gender", "Gender", "Respondent Gender", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["vt_type"] = _get(df, "VT type", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    out["center_name"] = _get(df, "VT Center Name", "CBE/School Name", "PB_Name", default="")
    out["rejection_reason"] = _get(df, "Rejection Reason", default="").fillna("").astype(str).str.strip()
    out["remarks"] = _get(df, "Remark", "Remarks", default="").fillna("").astype(str).str.strip()

    surveyor = _get(df, "Surveyor Name", "Surveyor_Name", default="")
    qc_by = _get(df, "QC By", "QA'd By", "QA_By", default="")
    out["staff_alias"] = surveyor.map(lambda x: _alias(x, "FIELD"))
    out["qc_alias"] = qc_by.map(lambda x: _alias(x, "QA"))

    out["background_audit"] = _numeric(_get(df, "Background Audit"))
    out["photo_quality"] = _numeric(_get(df, "Photo Quality"))
    out["audio_quality"] = _numeric(_get(df, "Audio Quality"))
    out["form_accuracy"] = _numeric(_get(df, "Form Accuracy"))
    out["form_rating"] = _numeric(_get(df, "Form Rating", "Enumerator Rating (1-5)"))
    out["language"] = _get(df, "Language", default="Unknown").fillna("Unknown").astype(str).str.strip().replace("", "Unknown")
    return out

def _project_df(df: pd.DataFrame, project: str, subsource: str, date_cols, status_cols) -> pd.DataFrame:
    out = _base_frame(df, project, subsource)

    date_series = None
    for col in date_cols:
        candidate = _get(df, col)
        if date_series is None:
            date_series = candidate
        else:
            mask = date_series.isna() | date_series.astype(str).str.strip().eq("")
            date_series = date_series.where(~mask, candidate)

    out["date"] = _parse_dates(date_series if date_series is not None else pd.Series(index=df.index, dtype=object))

    status_series = None
    for col in status_cols:
        candidate = _get(df, col)
        if status_series is None:
            status_series = candidate
        else:
            mask = status_series.isna() | status_series.astype(str).str.strip().eq("")
            status_series = status_series.where(~mask, candidate)

    out["status"] = (status_series if status_series is not None else pd.Series(index=df.index)).map(_status)
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.to_period("M").dt.to_timestamp()
    out["day"] = out["date"].dt.normalize()
    out["weekday"] = out["date"].dt.day_name()
    out["is_approved"] = out["status"].eq("Approved")
    out["is_rejected"] = out["status"].eq("Rejected")
    out["is_pending"] = out["status"].isin(["Pending", "Unreviewed"])

    return out

def build_master_dataset(frames: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, dict]:
    parts = []

    for project in ["CBE", "Public Schools"]:
        df = frames.get(project, pd.DataFrame())
        if not df.empty:
            parts.append(_project_df(df, project, project, ["Survey_Date"], ["Status"]))

    for project in ["ECE", "TLS"]:
        df = frames.get(project, pd.DataFrame())
        if not df.empty:
            parts.append(_project_df(df, project, project, ["Survey_Date"], ["Status"]))

    vt = frames.get("VT", pd.DataFrame())
    if not vt.empty:
        parts.append(_project_df(vt, "VT", "VT Main", ["Survey Date"], ["QA Status"]))

    kii = frames.get("VT_KII_FGD", pd.DataFrame())
    if not kii.empty:
        k = _project_df(kii, "VT", "VT KII/FGD", ["Received Date", "Date Received"], ["QA_Status"])
        # Ignore completely empty structural rows.
        k = k[
            k["record_id"].notna()
            & (
                k["tool_type"].astype(str).str.strip().ne("Unknown")
                | k["province"].astype(str).str.strip().ne("Unknown")
            )
        ].copy()
        k["tool_type"] = k["tool_type"].replace({"FGDs": "FGD"})
        parts.append(k)

    moraa = frames.get("Moraa", pd.DataFrame())
    if not moraa.empty:
        m = _project_df(moraa, "Moraa", "Moraa", ["SubmissionDate"], ["Status", "phone_response_short"])
        parts.append(m)

    if not parts:
        return pd.DataFrame(), {"rows": 0}

    master = pd.concat(parts, ignore_index=True, sort=False)

    master["province"] = master["province"].replace({
        "Herat": "Hirat",
        "Helmand": "Hilmand",
    })
    master["status"] = master["status"].where(
        master["status"].isin(["Approved", "Rejected", "Pending", "Unreviewed"]),
        "Unreviewed",
    )
    master["is_approved"] = master["status"].eq("Approved")
    master["is_rejected"] = master["status"].eq("Rejected")
    master["is_pending"] = master["status"].isin(["Pending", "Unreviewed"])

    meta = {
        "rows": len(master),
        "projects": sorted(master["project"].dropna().unique().tolist()),
        "dated_rows": int(master["date"].notna().sum()),
    }
    return master, meta

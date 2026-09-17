from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .config import SPREADSHEET_ID, SHEET_RANGES

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]

def _service_account_info() -> dict:
    if "gcp_service_account" not in st.secrets:
        raise RuntimeError(
            "Missing [gcp_service_account] in Streamlit Secrets. "
            "Copy the structure from .streamlit/secrets.example.toml."
        )
    return dict(st.secrets["gcp_service_account"])

@st.cache_data(ttl=300, show_spinner=False)
def _batch_get_values(spreadsheet_id: str, credentials_json: str):
    import json

    info = json.loads(credentials_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    result = (
        service.spreadsheets()
        .values()
        .batchGet(
            spreadsheetId=spreadsheet_id,
            ranges=list(SHEET_RANGES.values()),
            valueRenderOption="UNFORMATTED_VALUE",
            dateTimeRenderOption="SERIAL_NUMBER",
            majorDimension="ROWS",
        )
        .execute()
    )
    return result

def _values_to_df(values: list) -> pd.DataFrame:
    if not values:
        return pd.DataFrame()

    header = [str(x).strip() for x in values[0]]
    width = len(header)
    rows = []

    for row in values[1:]:
        row = list(row)
        if len(row) < width:
            row.extend([None] * (width - len(row)))
        rows.append(row[:width])

    if not header:
        return pd.DataFrame()

    # Ensure unique column names.
    seen = {}
    unique_header = []
    for col in header:
        base = col or "Unnamed"
        n = seen.get(base, 0)
        seen[base] = n + 1
        unique_header.append(base if n == 0 else f"{base}_{n+1}")

    return pd.DataFrame(rows, columns=unique_header)

def load_google_sheet() -> Tuple[Dict[str, pd.DataFrame], dict]:
    import json

    info = _service_account_info()
    result = _batch_get_values(SPREADSHEET_ID, json.dumps(info, sort_keys=True))

    value_ranges = result.get("valueRanges", [])
    frames = {}

    for sheet_name, value_range in zip(SHEET_RANGES.keys(), value_ranges):
        values = value_range.get("values", [])
        frames[sheet_name] = _values_to_df(values)

    meta = {
        "spreadsheet_id": SPREADSHEET_ID,
        "loaded_sheets": list(frames.keys()),
        "sheet_count": len(frames),
    }
    return frames, meta

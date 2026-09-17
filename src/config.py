APP_TITLE = "UNICEF Education Portfolio"
APP_SUBTITLE = "Advanced public monitoring dashboard • live project delivery • QA/QC • geography • implementation intelligence"

SPREADSHEET_ID = "1wtRzWbJ5uGdc5pqc9KJnauPuFnVQauL31VE9mX-LJ_U"

PROJECTS = ["CBE", "Public Schools", "Moraa", "VT", "TLS", "ECE"]

# Official / configured 2026 targets.
# Live counts, statuses, trends and quality metrics are all computed from the project tabs.
SCOPES = {
    "CBE": 900,
    "Public Schools": 1477,
    "Moraa": 1572,
    "VT": 4835,
    "TLS": 400,
    "ECE": 200,
}

DEFAULT_YEAR = 2026

SHEET_RANGES = {
    "CBE": "'CBE'!A:U",
    "Public Schools": "'Public Schools'!A:U",
    "ECE": "'ECE'!A:S",
    "TLS": "'TLS'!A:S",
    "VT": "'VT'!A:S",
    "VT_KII_FGD": "'VT_KII_FGD'!A:W",
    "Moraa": "'Moraa'!A:R",
}

PUBLIC_MODE = True

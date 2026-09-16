# UNICEF Advanced Streamlit Cloud Dashboard

This package is a production-oriented public dashboard connected directly to the Google Sheet:

`1wtRzWbJ5uGdc5pqc9KJnauPuFnVQauL31VE9mX-LJ_U`

## Critical data architecture

The app reads **only the internal project tabs** of that Google Sheet:

- `CBE`
- `Public Schools`
- `ECE`
- `TLS`
- `VT`
- `VT_KII_FGD`
- `Moraa`

It does **not** read `Dashboard`, `Dashboard_Data`, or the external source spreadsheets.

That means the Google Sheet remains the central data-control layer, while Streamlit is the modern public visualization layer.

## Public-dashboard privacy

The app is designed for a public deployment.

For that reason:
- Beneficiary names and phone numbers are not displayed.
- Field staff and QA staff are pseudonymized in performance charts.
- The public record explorer only exposes non-sensitive operational fields.
- Google service-account credentials stay in Streamlit Secrets and never go into GitHub.

## Main capabilities

### Executive overview
- Total scope
- Received
- Approved
- Rejected
- Pending QA
- Overall completion
- Approval rate
- QC reviewed rate
- Remaining scope
- Automatic management insights
- Portfolio health matrix

### Project filtering
The user can switch between:
- All Projects
- CBE
- Public Schools
- Moraa
- VT
- TLS
- ECE

The selected project is also stored in the URL query parameter so a project view can be shared.

### Dedicated project deep dive
Each project gets a complete dashboard.

- CBE / Public Schools / ECE / TLS:
  - monthly trend
  - province status
  - QA component profile
  - rejection Pareto
  - tool/instrument mix
  - QA reviewer distribution

- VT:
  - VT tool risk map
  - tool-level received / approved / rejected / pending
  - province analysis
  - monthly trend
  - rejection Pareto
  - KII / FGD automatically included under VT

- Moraa:
  - phase analysis
  - discipline analysis
  - gender analysis
  - phase → discipline → status sunburst
  - monthly trend

### Quality intelligence
- Rejection Pareto
- Field-staff performance map
- Approval / rejection / backlog metrics
- Missing rejection reason
- Future-dated records
- Undated VT KII/FGD

### Geography and trends
- Province status mix
- Monthly received / approved / rejected / pending
- Province performance table

### Public data explorer
- Privacy-safe filtered rows
- CSV download
- No beneficiary PII

## Google Sheets connection

The app uses the Google Sheets API through a **read-only service account**.

### 1. Create a Google Cloud project
Enable:

`Google Sheets API`

### 2. Create a Service Account
Download its JSON key.

### 3. Share the Google Sheet
Share the Google Sheet with the service-account email as **Viewer**.

### 4. Configure Streamlit Secrets
In Streamlit Community Cloud:

`App → Settings → Secrets`

Copy the structure from:

`.streamlit/secrets.example.toml`

and replace the placeholders with the real service-account values.

Never upload the real private key to GitHub.

## Deploy to Streamlit Community Cloud

1. Create a private GitHub repository.
2. Upload the project files.
3. Go to Streamlit Community Cloud.
4. Create a new app.
5. Select the repository.
6. Main file: `app.py`
7. Add the Secrets.
8. Deploy.

## Local run

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

## Cache / refresh behavior

The Google Sheet is cached for 5 minutes for performance.

The user can click:

`Refresh live data`

to clear the cache immediately.

## Scope targets

The current 2026 scope targets are stored in:

`src/config.py`

They are reference targets only. All live counts, statuses, trends and QA metrics are calculated from the Google Sheet project tabs.

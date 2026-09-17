# UNICEF Ultra-Modern Streamlit Portfolio Intelligence

A production-ready public Streamlit dashboard connected directly to the internal project tabs of the central Google Sheet.

## Data source

The app reads only these tabs from Google Sheet `1wtRzWbJ5uGdc5pqc9KJnauPuFnVQauL31VE9mX-LJ_U`:

- CBE
- Public Schools
- ECE
- TLS
- VT
- VT_KII_FGD
- Moraa

The app does **not** calculate KPI values from `Dashboard` or `Dashboard_Data`.

## Major capabilities

- Dark-only premium public interface
- Responsive laptop and large-monitor layout
- Executive KPI layer
- Scope-completion gauge
- QA-status donut
- Portfolio performance radar
- Health matrix
- Scope treemap
- Portfolio delivery funnel
- Remaining-scope pressure chart
- Monthly spline trends
- Collection intensity heatmap
- VT tool risk map
- Province quality-vs-volume analytics
- Rejection Pareto
- Field-staff performance map with pseudonymized identities
- QA reviewer workload/outcome chart
- Moraa phase/discipline/status sunburst
- Project-specific deep dives
- Province and district analytics
- Privacy-safe public data explorer
- CSV download
- URL-shareable project view
- 5-minute live Google Sheets cache plus manual refresh

## Dark-only behavior

This package pins `streamlit==1.63.0`, defines both light and dark variants with the same dark palette, uses minimal toolbar mode, and adds a CSS dark lock. Public viewers therefore remain in the dark visual system even if their device/browser preference is light.

## Public privacy

Beneficiary names and phone numbers are not included in the public explorer. Field and QA staff identities are pseudonymized in performance views.

## Deployment

1. Upload the entire project to a private GitHub repository.
2. Enable Google Sheets API in Google Cloud.
3. Create a service account and JSON key.
4. Share the central Google Sheet with the service-account email as Viewer.
5. Put the credential values into Streamlit Cloud → App → Settings → Secrets, using `.streamlit/secrets.example.toml` as the exact structure.
6. Set the Streamlit main file to `app.py`.
7. Deploy and reboot once after the first deployment.

Never commit a real `secrets.toml` or private key to GitHub.

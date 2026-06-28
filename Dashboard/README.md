# Auto Radar Dashboard v1.0

Read-only operational Dashboard for approved Repository records.

## Refresh Data

```powershell
python Scripts/Dashboard/build_dashboard_data.py
```

## Open

Open `Dashboard/index.html` in a browser. The generated data is embedded in
`Dashboard/dashboard-data.js`, so no Runtime service is required.

## Boundary

The Dashboard does not calculate Opportunity Score, Confidence, Strategy,
regime, money flow, or trading actions. Missing approved records are shown as
unavailable.

# auto-radar-global-v2

Auto Radar Global v2 dashboard.

Sprint 3 adds Data Pipeline v1:

- Dashboard reads `data/auto_radar_daily_brief.json`
- `/data/current` returns the current full payload
- `/pipeline/run` refreshes the payload
- Scheduler runs daily at Asia/Taipei 08:30

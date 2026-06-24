# Auto Radar Global v2 - Project State

## Current Status
已完成第一版可視化 Dashboard：
- Render 已上線
- GitHub 已連接
- FastAPI 正常
- /dashboard 可顯示
- 已有市場模式、題材分數、配置、停損停利、風險事件

## Current URL
https://auto-radar-global-v2.onrender.com/dashboard

## Completed Modules
- Theme Tree v1
- Lifecycle Stage v1
- Theme Score Framework v1
- Stage Transition Engine v1
- Confidence Framework v1
- Daily Brief Engine v1
- Dashboard Prototype v1

## Core Rule
風控 > 題材 > 個股

## Current Dashboard Output
使用者打開 Dashboard 要看到：
1. 現在市場模式
2. 主線題材
3. 下一個接棒題材
4. 禁止碰的題材
5. 建議持股比例
6. 進場條件
7. 停損
8. 停利
9. 重大事件風險

## Known Issues
- Render Free 會休眠，第一次打開會慢
- 目前資料是寫死的假資料
- 尚未接真實資料 API
- 尚未接 Telegram 推播
- 尚未接資料庫

## Next Sprint
Sprint 3：Data Pipeline v1

目標：
把目前寫死的資料，改成每日自動更新。

優先資料來源：
1. 台股價格
2. 美股 AI 相關指標
3. 台股法人買賣超
4. 新聞題材
5. 重大事件日曆

## Next Immediate Task
建立：
- Docs/Sprint_2_Summary.md
- data/daily_brief.json
- API 讀取 JSON，而不是寫死在 main.py

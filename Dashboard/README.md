# Auto Radar 儀表板 v1.0

供每日使用的知識庫唯讀操作介面。

## 更新資料

```powershell
python Scripts/Dashboard/build_dashboard_data.py
```

## 開啟

以瀏覽器開啟 `Dashboard/index.html`。產生的資料位於
`Dashboard/dashboard-data.js`，不依賴正式執行層服務。

## 邊界

儀表板不計算機會分數、信心度、策略、市場狀態、資金流或交易行動。
尚未建立的核准紀錄會顯示為等待資料。

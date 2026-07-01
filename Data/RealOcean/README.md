# Real Ocean

Status: Shadow Runtime Only

本目錄只保存 Provider Registry metadata，不保存 API key、User-Agent 聯絡資訊
或 Runtime 可直接呼叫的端點。

環境設定：

- `FRED_API_KEY`: FRED 官方 API key。
- `SEC_USER_AGENT`: 符合 SEC fair-access 規範的應用名稱與聯絡方式。
- `SEC_EDGAR_CIKS`: 選用，以逗號分隔的 CIK。

正式資料路徑為 Provider Registry → Validate → Normalize → Snapshot v3。
Fixture 只可用於 Replay 與 Test。

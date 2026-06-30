# Market Provider Fixtures

Status: Archived Replay Fixtures

Model Impact: Provider data only, not production

本目錄保存 Real Data Foundation 的 archived provider fixtures。目前資料用於介面、品質閘門與 Replay 驗證，不宣稱為即時市場資料。

- `replay_2026-07-02.json`：六個 Provider 的固定輸入與 Replay metadata。
- `manual_outcome_2026-07-02.json`：Replay 使用的人工 Outcome。

未來 API adapter 必須先轉換成相同 Provider Record，再通過 Data Quality Engine；Runtime 不得直接存取 API。

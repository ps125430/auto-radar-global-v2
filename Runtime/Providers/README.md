# Market Provider Layer

Status: Shadow Real Data Foundation

Model Impact: Provider data only, not production

## Data Flow

```text
Archived Provider Payload
  -> Provider Interface
  -> Data Quality Engine
  -> Market Snapshot Builder
  -> Market Snapshot Reader
  -> Evidence / Shadow Replay
```

## Providers

- `TaiwanProvider`
- `USProvider`
- `MacroProvider`
- `NewsProvider`
- `ETFProvider`
- `MockProvider`

目前所有 Provider 都是無網路 archived-payload adapter。Runtime 不含 API client，也不得直接呼叫未來外部 API。

## Quality Gate

Snapshot 建立前必須檢查：

- Missing
- Duplicate
- Invalid
- Outlier
- Timestamp

任一錯誤立即停止，不產生部分 Snapshot。

## Snapshot Boundary

Runtime market data 只能透過 `MarketSnapshotReader` 讀取已通過 Quality PASS 的 Snapshot。Provider instance 不得傳入 North Star Runtime。

## Write Boundary

- Provider 與 Quality Engine 不寫檔。
- Evidence Collector 只產生 Runtime Evidence candidate。
- Replay 只能透過 `ArtifactWriter` 寫入 `Runtime/Artifacts/`。
- 不得寫入 Knowledge、Data、Dashboard、Scoring、Strategy 或 Production Runtime。

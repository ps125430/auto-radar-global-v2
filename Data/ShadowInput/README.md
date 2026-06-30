# Shadow Input

Status: Shadow Input Candidate

Model Impact: Shadow only, not production

## Purpose

本目錄保存 North Star Shadow Runtime 的受控輸入包，用於驗證：

`Input → Runtime Projection → Dashboard`

## Boundary

- 輸入內容不代表正式市場研究結論。
- `display_score` 是測試輸入值，不是 Runtime 計算結果。
- 不得由本目錄建立交易指令。
- 不得自動寫回 Repository。
- 所有 Evidence reference 必須指向已存在的唯讀資料。

## Current Pack

`sample_real_input_v1.json` 是 E-137 建立的第一批半真實測試資料，涵蓋 AI 基礎建設、HBM、散熱、電力與 CPO 語境。

`manual_outcome_2026-06-30.json` 是 E-147 的人工 Outcome 範例，包含價格結果、實際星等、人工 Engine diagnostics 與 Reflection context。它不是 API 資料，也不代表正式市場事實。

window.AUTO_RADAR_DASHBOARD_DATA = {
  "capital_flow": {
    "edges": [
      {
        "edge_type": "SHADOW_FLOWS_TO",
        "source": "SHADOW-FLOW-01",
        "status": "shadow_input_candidate",
        "target": "SHADOW-FLOW-02"
      },
      {
        "edge_type": "SHADOW_FLOWS_TO",
        "source": "SHADOW-FLOW-02",
        "status": "shadow_input_candidate",
        "target": "SHADOW-FLOW-03"
      },
      {
        "edge_type": "SHADOW_FLOWS_TO",
        "source": "SHADOW-FLOW-03",
        "status": "shadow_input_candidate",
        "target": "SHADOW-FLOW-04"
      },
      {
        "edge_type": "SHADOW_FLOWS_TO",
        "source": "SHADOW-FLOW-04",
        "status": "shadow_input_candidate",
        "target": "SHADOW-FLOW-05"
      }
    ],
    "message": null,
    "nodes": [
      {
        "category": "Shadow 資金路徑",
        "id": "SHADOW-FLOW-01",
        "name": "美國半導體",
        "status": "shadow_input_candidate"
      },
      {
        "category": "Shadow 資金路徑",
        "id": "SHADOW-FLOW-02",
        "name": "台灣 AI 供應鏈",
        "status": "shadow_input_candidate"
      },
      {
        "category": "Shadow 資金路徑",
        "id": "SHADOW-FLOW-03",
        "name": "散熱",
        "status": "shadow_input_candidate"
      },
      {
        "category": "Shadow 資金路徑",
        "id": "SHADOW-FLOW-04",
        "name": "HBM",
        "status": "shadow_input_candidate"
      },
      {
        "category": "Shadow 資金路徑",
        "id": "SHADOW-FLOW-05",
        "name": "CPO",
        "status": "shadow_input_candidate"
      }
    ],
    "status": "已有資料"
  },
  "meta": {
    "data_gaps": [
      "策略信心度"
    ],
    "generated_at": "2026-07-02T21:00:00+00:00",
    "mode": "知識庫唯讀",
    "repository_status": "通過",
    "sources": [
      "每日預測草稿",
      "市場認知草稿",
      "模式候選清冊",
      "驗證案例清冊",
      "證據沙盒",
      "知識圖譜",
      "全域驗證報告",
      "Shadow Runtime 半真實輸入包"
    ],
    "validation_errors": 0,
    "validation_warnings": 1
  },
  "opportunities": [
    {
      "crowded": null,
      "evidence_ids": [
        "EV-102",
        "EV-104"
      ],
      "expectation_stars": 5,
      "explainability": {
        "evidence": [
          "EV-102",
          "EV-104"
        ],
        "history": [],
        "money": "資料流展示用途，尚待人工市場驗證。",
        "risk": "價格反應可能早於基本面驗證。",
        "why_score": "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。"
      },
      "id": "SHADOW-OPP-001",
      "money_flow": "半真實 Shadow 輸入",
      "name": "散熱",
      "opportunity_score": 84,
      "risk": "價格反應可能早於基本面驗證。",
      "score_status": "sample_shadow_input",
      "source_cases": [],
      "status": "Shadow 候選",
      "why_now": "Archived Replay 將散熱列為第一候選，不代表正式評分。",
      "window": "5 天"
    },
    {
      "crowded": null,
      "evidence_ids": [
        "EV-101",
        "EV-103"
      ],
      "expectation_stars": 4,
      "explainability": {
        "evidence": [
          "EV-101",
          "EV-103"
        ],
        "history": [],
        "money": "資料流展示用途，尚待人工市場驗證。",
        "risk": "規格升級預期可能已部分反映。",
        "why_score": "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。"
      },
      "id": "SHADOW-OPP-002",
      "money_flow": "半真實 Shadow 輸入",
      "name": "HBM",
      "opportunity_score": 81,
      "risk": "規格升級預期可能已部分反映。",
      "score_status": "sample_shadow_input",
      "source_cases": [],
      "status": "Shadow 候選",
      "why_now": "Archived Replay 將 HBM 列為第二候選，不代表正式評分。",
      "window": "5 天"
    },
    {
      "crowded": null,
      "evidence_ids": [
        "EV-105"
      ],
      "expectation_stars": 3,
      "explainability": {
        "evidence": [
          "EV-105"
        ],
        "history": [],
        "money": "資料流展示用途，尚待人工市場驗證。",
        "risk": "商用導入時間仍不確定。",
        "why_score": "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。"
      },
      "id": "SHADOW-OPP-003",
      "money_flow": "半真實 Shadow 輸入",
      "name": "CPO",
      "opportunity_score": 72,
      "risk": "商用導入時間仍不確定。",
      "score_status": "sample_shadow_input",
      "source_cases": [],
      "status": "Shadow 候選",
      "why_now": "Archived Replay 將 CPO 列為次級擴散候選。",
      "window": "10 天"
    }
  ],
  "regime": {
    "dominant_narrative": null,
    "fallback": "等待核准資料建立。",
    "macro": "風險偏好中性偏多",
    "market_mood": null,
    "micro": "主線延續但子題材分化",
    "sector": "半導體與 AI 基礎建設偏強",
    "status": "草稿"
  },
  "repository": {
    "evidence_records": 5,
    "graph_edges": 0,
    "graph_nodes": 0,
    "pattern_candidates": 3,
    "verified_cases": 5,
    "warnings": [
      "信心度知識庫尚未建立。"
    ]
  },
  "shadow_runtime": {
    "contract_version": "1.0",
    "explain": {
      "chain_id": "EXPLAIN-DASHBOARD-20260702",
      "decision": "NSD-DASHBOARD-20260702",
      "direction": "AI 基礎建設接力觀察",
      "edges": [],
      "layers": {
        "capital_flow": [
          "SHADOW-FLOW-01",
          "SHADOW-FLOW-02",
          "SHADOW-FLOW-03",
          "SHADOW-FLOW-04",
          "SHADOW-FLOW-05"
        ],
        "decision": [
          "NSD-DASHBOARD-20260702"
        ],
        "direction": [],
        "evidence": [
          "EV-101",
          "EV-102",
          "EV-103",
          "EV-104",
          "EV-105"
        ],
        "regime": [
          "總經：風險偏好中性偏多",
          "產業：半導體與 AI 基礎建設偏強",
          "市場：主線延續但子題材分化"
        ],
        "repository": [
          "Dashboard/dashboard-data.js"
        ]
      },
      "missing_refs": [],
      "nodes": [
        {
          "available": true,
          "layer": "decision",
          "node_id": "decision:NSD-DASHBOARD",
          "reference": "NSD-DASHBOARD-20260702"
        },
        {
          "available": true,
          "layer": "evidence",
          "node_id": "evidence:EV-101",
          "reference": "EV-101"
        },
        {
          "available": true,
          "layer": "evidence",
          "node_id": "evidence:EV-102",
          "reference": "EV-102"
        },
        {
          "available": true,
          "layer": "evidence",
          "node_id": "evidence:EV-103",
          "reference": "EV-103"
        },
        {
          "available": true,
          "layer": "evidence",
          "node_id": "evidence:EV-104",
          "reference": "EV-104"
        },
        {
          "available": true,
          "layer": "evidence",
          "node_id": "evidence:EV-105",
          "reference": "EV-105"
        },
        {
          "available": true,
          "layer": "pattern",
          "node_id": "pattern:market-regime:1",
          "reference": "總經：風險偏好中性偏多"
        },
        {
          "available": true,
          "layer": "pattern",
          "node_id": "pattern:market-regime:2",
          "reference": "產業：半導體與 AI 基礎建設偏強"
        },
        {
          "available": true,
          "layer": "pattern",
          "node_id": "pattern:market-regime:3",
          "reference": "市場：主線延續但子題材分化"
        },
        {
          "available": true,
          "layer": "experience",
          "node_id": "experience:SHADOW-FLOW-01",
          "reference": "SHADOW-FLOW-01"
        },
        {
          "available": true,
          "layer": "experience",
          "node_id": "experience:SHADOW-FLOW-02",
          "reference": "SHADOW-FLOW-02"
        },
        {
          "available": true,
          "layer": "experience",
          "node_id": "experience:SHADOW-FLOW-03",
          "reference": "SHADOW-FLOW-03"
        },
        {
          "available": true,
          "layer": "experience",
          "node_id": "experience:SHADOW-FLOW-04",
          "reference": "SHADOW-FLOW-04"
        },
        {
          "available": true,
          "layer": "experience",
          "node_id": "experience:SHADOW-FLOW-05",
          "reference": "SHADOW-FLOW-05"
        },
        {
          "available": true,
          "layer": "repository",
          "node_id": "repository:dashboard-projection",
          "reference": "Dashboard/dashboard-data.js"
        }
      ]
    },
    "last_run": "2026-07-02T21:00:00+00:00",
    "mode": {
      "label": "Shadow Runtime",
      "production_authorized": false,
      "repository": "Read Only",
      "schema": "PASS",
      "status": "Healthy"
    },
    "model_impact": "shadow_candidate_not_production",
    "status": "shadow_dashboard_projection",
    "timeline": {
      "today": "散熱與 HBM 成為 Replay Top2，CPO 位於第三順位。",
      "tomorrow": "只觀察 Evidence 與資金鏈是否延續，不自動升級。",
      "yesterday": "AI 基礎建設維持主線，資金開始向供應鏈延伸。"
    },
    "today": {
      "captain_mission": "觀察散熱與 HBM 是否延續，CPO 維持次級候選。",
      "daily_brief": "今日北極星：AI 基礎建設接力觀察。今日航向：觀察散熱與 HBM 是否延續，CPO 維持次級候選。今日 Top3：散熱, HBM, CPO。今日風險：Provider fixture 不是即時 API 資料、Replay 不得產生正式交易訊號、所有輸出仍需人工 Review。",
      "direction": "AI 基礎建設接力觀察",
      "forbidden_zone": [
        "不以 Replay 結果取代即時資料。",
        "不將顯示分數視為 Production Scoring。",
        "不自動寫回 Knowledge Repository。"
      ],
      "market_story": "今日 Shadow 方向為 AI 基礎建設接力觀察；第一候選為 散熱，主要風險是 Provider fixture 不是即時 API 資料。",
      "risk_summary": [
        "Provider fixture 不是即時 API 資料。",
        "Replay 不得產生正式交易訊號。",
        "所有輸出仍需人工 Review。"
      ],
      "top3": [
        "散熱",
        "HBM",
        "CPO"
      ],
      "why_now": "Archived replay fixture 顯示半導體與台灣 AI 供應鏈仍有資金語境；內容只用於重播驗證。",
      "window": "5 天"
    },
    "waiting_message": "Waiting for today's shadow run..."
  },
  "strategy": {
    "confidence": null,
    "fallback": "等待核准資料建立。",
    "name": "AI 基礎建設接力觀察",
    "status": "草稿",
    "why_now": "Archived replay fixture 顯示半導體與台灣 AI 供應鏈仍有資金語境；內容只用於重播驗證。",
    "window": "5 天"
  },
  "tactical": {
    "avoid": [],
    "fallback": "等待核准資料建立。",
    "risk": [
      "Provider fixture 不是即時 API 資料。",
      "Replay 不得產生正式交易訊號。",
      "所有輸出仍需人工 Review。"
    ],
    "strategy": "AI 基礎建設接力觀察",
    "watch": [
      "SHADOW-OPP-001 · 等待研究審查",
      "SHADOW-OPP-002 · 等待研究審查",
      "SHADOW-OPP-003 · 等待研究審查"
    ],
    "window": "5 天"
  }
};

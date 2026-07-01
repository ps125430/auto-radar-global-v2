window.AUTO_RADAR_DASHBOARD_DATA = {
  "meta": {
    "generated_at": "2026-07-01T08:29:59.246401+00:00",
    "mode": "知識庫唯讀",
    "repository_status": "通過",
    "validation_errors": 0,
    "validation_warnings": 1,
    "data_gaps": [
      "策略信心度"
    ],
    "sources": [
      "每日預測草稿",
      "市場認知草稿",
      "模式候選清冊",
      "驗證案例清冊",
      "證據沙盒",
      "知識圖譜",
      "全域驗證報告",
      "Shadow Runtime 半真實輸入包",
      "Living Ocean 官方來源快照"
    ]
  },
  "strategy": {
    "name": "AI 基礎建設供應鏈",
    "confidence": null,
    "window": "5 天",
    "why_now": "半真實測試輸入顯示資金語境由 AI 晶片延伸至記憶體、散熱與電力基礎設施；所有內容仍待人工驗證。",
    "status": "草稿",
    "fallback": "等待核准資料建立。"
  },
  "regime": {
    "macro": "風險偏好中性偏多",
    "sector": "AI 基礎建設維持主線",
    "micro": "上游強勢，延伸題材分化",
    "market_mood": null,
    "dominant_narrative": null,
    "status": "草稿",
    "fallback": "等待核准資料建立。"
  },
  "opportunities": [
    {
      "id": "SHADOW-OPP-001",
      "name": "HBM",
      "opportunity_score": 86,
      "expectation_stars": 5,
      "score_status": "sample_shadow_input",
      "window": "5 天",
      "money_flow": "半真實 Shadow 輸入",
      "risk": "市場已部分反映規格升級預期。",
      "crowded": null,
      "why_now": "半真實輸入將 HBM 標記為 AI 基礎建設的第一層供應瓶頸候選。",
      "status": "Shadow 候選",
      "source_cases": [],
      "evidence_ids": [
        "EV-101",
        "EV-103"
      ],
      "explainability": {
        "why_score": "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。",
        "evidence": [
          "EV-101",
          "EV-103"
        ],
        "money": "資料流展示用途，尚待人工市場驗證。",
        "history": [],
        "risk": "市場已部分反映規格升級預期。"
      }
    },
    {
      "id": "SHADOW-OPP-002",
      "name": "散熱",
      "opportunity_score": 82,
      "expectation_stars": 4,
      "score_status": "sample_shadow_input",
      "window": "5 天",
      "money_flow": "半真實 Shadow 輸入",
      "risk": "題材擴散可能快於實際訂單驗證。",
      "crowded": null,
      "why_now": "半真實輸入將散熱標記為高功耗 AI 系統的接力候選。",
      "status": "Shadow 候選",
      "source_cases": [],
      "evidence_ids": [
        "EV-102",
        "EV-104"
      ],
      "explainability": {
        "why_score": "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。",
        "evidence": [
          "EV-102",
          "EV-104"
        ],
        "money": "資料流展示用途，尚待人工市場驗證。",
        "history": [],
        "risk": "題材擴散可能快於實際訂單驗證。"
      }
    },
    {
      "id": "SHADOW-OPP-003",
      "name": "電力",
      "opportunity_score": 78,
      "expectation_stars": 4,
      "score_status": "sample_shadow_input",
      "window": "10 天",
      "money_flow": "半真實 Shadow 輸入",
      "risk": "資本支出時程與政策落地仍有延遲風險。",
      "crowded": null,
      "why_now": "半真實輸入將資料中心供電需求列為較長觀察窗候選。",
      "status": "Shadow 候選",
      "source_cases": [],
      "evidence_ids": [
        "EV-103",
        "EV-105"
      ],
      "explainability": {
        "why_score": "顯示分數來自半真實測試輸入，不是 Runtime 計算結果。",
        "evidence": [
          "EV-103",
          "EV-105"
        ],
        "money": "資料流展示用途，尚待人工市場驗證。",
        "history": [],
        "risk": "資本支出時程與政策落地仍有延遲風險。"
      }
    }
  ],
  "capital_flow": {
    "status": "已有資料",
    "nodes": [
      {
        "id": "SHADOW-FLOW-01",
        "name": "美國 AI 基礎建設",
        "category": "Shadow 資金路徑",
        "status": "shadow_input_candidate"
      },
      {
        "id": "SHADOW-FLOW-02",
        "name": "HBM",
        "category": "Shadow 資金路徑",
        "status": "shadow_input_candidate"
      },
      {
        "id": "SHADOW-FLOW-03",
        "name": "散熱",
        "category": "Shadow 資金路徑",
        "status": "shadow_input_candidate"
      },
      {
        "id": "SHADOW-FLOW-04",
        "name": "電力",
        "category": "Shadow 資金路徑",
        "status": "shadow_input_candidate"
      },
      {
        "id": "SHADOW-FLOW-05",
        "name": "CPO",
        "category": "Shadow 資金路徑",
        "status": "shadow_input_candidate"
      }
    ],
    "edges": [
      {
        "source": "SHADOW-FLOW-01",
        "target": "SHADOW-FLOW-02",
        "edge_type": "SHADOW_FLOWS_TO",
        "status": "shadow_input_candidate"
      },
      {
        "source": "SHADOW-FLOW-02",
        "target": "SHADOW-FLOW-03",
        "edge_type": "SHADOW_FLOWS_TO",
        "status": "shadow_input_candidate"
      },
      {
        "source": "SHADOW-FLOW-03",
        "target": "SHADOW-FLOW-04",
        "edge_type": "SHADOW_FLOWS_TO",
        "status": "shadow_input_candidate"
      },
      {
        "source": "SHADOW-FLOW-04",
        "target": "SHADOW-FLOW-05",
        "edge_type": "SHADOW_FLOWS_TO",
        "status": "shadow_input_candidate"
      }
    ],
    "message": null
  },
  "tactical": {
    "strategy": "AI 基礎建設供應鏈",
    "risk": [
      "題材價格可能已提前反映。",
      "目前證據為 Sandbox 追溯資料，不代表市場事實已驗證。",
      "Production Runtime 與交易指令仍未授權。"
    ],
    "window": "5 天",
    "watch": [
      "SHADOW-OPP-001 · 等待研究審查",
      "SHADOW-OPP-002 · 等待研究審查",
      "SHADOW-OPP-003 · 等待研究審查"
    ],
    "avoid": [],
    "fallback": "等待核准資料建立。"
  },
  "repository": {
    "pattern_candidates": 3,
    "verified_cases": 5,
    "evidence_records": 5,
    "graph_nodes": 0,
    "graph_edges": 0,
    "warnings": [
      "信心度知識庫尚未建立。"
    ]
  },
  "shadow_runtime": {
    "contract_version": "1.0",
    "status": "shadow_dashboard_projection",
    "model_impact": "shadow_candidate_not_production",
    "waiting_message": "Waiting for today's shadow run...",
    "last_run": "2026-07-01T08:29:59.246401+00:00",
    "mode": {
      "label": "Shadow Runtime",
      "status": "Healthy",
      "schema": "PASS",
      "repository": "Read Only",
      "production_authorized": false
    },
    "today": {
      "direction": "AI 基礎建設供應鏈",
      "captain_mission": "聚焦 HBM 與散熱的資金接力，CPO 與電力題材維持觀察。",
      "market_story": "今日 Shadow 方向為 AI 基礎建設供應鏈；第一候選為 HBM，主要風險是 題材價格可能已提前反映。",
      "daily_brief": "今日北極星：AI 基礎建設供應鏈。今日航向：聚焦 HBM 與散熱的資金接力，CPO 與電力題材維持觀察。今日 Top3：HBM, 散熱, 電力。今日風險：題材價格可能已提前反映、目前證據為 Sandbox 追溯資料，不代表市場事實已驗證、Production Runtime 與交易指令仍未授權。",
      "risk_summary": [
        "題材價格可能已提前反映。",
        "目前證據為 Sandbox 追溯資料，不代表市場事實已驗證。",
        "Production Runtime 與交易指令仍未授權。"
      ],
      "window": "5 天",
      "why_now": "半真實測試輸入顯示資金語境由 AI 晶片延伸至記憶體、散熱與電力基礎設施；所有內容仍待人工驗證。",
      "top3": [
        "HBM",
        "散熱",
        "電力"
      ],
      "forbidden_zone": [
        "不追逐缺乏 Evidence reference 的題材。",
        "不將 Shadow 顯示分數視為正式評分。",
        "不依本資料包建立交易指令。"
      ]
    },
    "timeline": {
      "yesterday": "AI 晶片主線維持，資金開始尋找供應鏈延伸題材。",
      "today": "HBM 與散熱成為主要接力候選，電力與 CPO 進入觀察。",
      "tomorrow": "觀察 HBM 與散熱是否維持接力，若 Evidence 未增加則不升級。"
    },
    "explain": {
      "chain_id": "EXPLAIN-DASHBOARD-20260701",
      "direction": "AI 基礎建設供應鏈",
      "decision": "NSD-DASHBOARD-20260701",
      "nodes": [
        {
          "node_id": "decision:NSD-DASHBOARD",
          "layer": "decision",
          "reference": "NSD-DASHBOARD-20260701",
          "available": true
        },
        {
          "node_id": "evidence:EV-101",
          "layer": "evidence",
          "reference": "EV-101",
          "available": true
        },
        {
          "node_id": "evidence:EV-102",
          "layer": "evidence",
          "reference": "EV-102",
          "available": true
        },
        {
          "node_id": "evidence:EV-103",
          "layer": "evidence",
          "reference": "EV-103",
          "available": true
        },
        {
          "node_id": "evidence:EV-104",
          "layer": "evidence",
          "reference": "EV-104",
          "available": true
        },
        {
          "node_id": "evidence:EV-105",
          "layer": "evidence",
          "reference": "EV-105",
          "available": true
        },
        {
          "node_id": "pattern:market-regime:1",
          "layer": "pattern",
          "reference": "總經：風險偏好中性偏多",
          "available": true
        },
        {
          "node_id": "pattern:market-regime:2",
          "layer": "pattern",
          "reference": "產業：AI 基礎建設維持主線",
          "available": true
        },
        {
          "node_id": "pattern:market-regime:3",
          "layer": "pattern",
          "reference": "市場：上游強勢，延伸題材分化",
          "available": true
        },
        {
          "node_id": "experience:SHADOW-FLOW-01",
          "layer": "experience",
          "reference": "SHADOW-FLOW-01",
          "available": true
        },
        {
          "node_id": "experience:SHADOW-FLOW-02",
          "layer": "experience",
          "reference": "SHADOW-FLOW-02",
          "available": true
        },
        {
          "node_id": "experience:SHADOW-FLOW-03",
          "layer": "experience",
          "reference": "SHADOW-FLOW-03",
          "available": true
        },
        {
          "node_id": "experience:SHADOW-FLOW-04",
          "layer": "experience",
          "reference": "SHADOW-FLOW-04",
          "available": true
        },
        {
          "node_id": "experience:SHADOW-FLOW-05",
          "layer": "experience",
          "reference": "SHADOW-FLOW-05",
          "available": true
        },
        {
          "node_id": "repository:dashboard-projection",
          "layer": "repository",
          "reference": "Dashboard/dashboard-data.js",
          "available": true
        }
      ],
      "edges": [],
      "missing_refs": [],
      "layers": {
        "direction": [],
        "decision": [
          "NSD-DASHBOARD-20260701"
        ],
        "regime": [
          "總經：風險偏好中性偏多",
          "產業：AI 基礎建設維持主線",
          "市場：上游強勢，延伸題材分化"
        ],
        "capital_flow": [
          "SHADOW-FLOW-01",
          "SHADOW-FLOW-02",
          "SHADOW-FLOW-03",
          "SHADOW-FLOW-04",
          "SHADOW-FLOW-05"
        ],
        "evidence": [
          "EV-101",
          "EV-102",
          "EV-103",
          "EV-104",
          "EV-105"
        ],
        "repository": [
          "Dashboard/dashboard-data.js"
        ]
      }
    }
  },
  "living_ocean": {
    "status": "shadow_real_ocean_monitor",
    "snapshot_version": "2026-07-01-MANUAL",
    "snapshot_hash": "7825a5dd78e42180a3064946a904ebf2318569b89f5cf3748a1c5c7ad409b29c",
    "generated_at": "2026-07-01T16:29:22.628734+08:00",
    "overall_status": "healthy",
    "health_score": 100,
    "evidence_coverage": 100,
    "sources": [
      {
        "error": null,
        "health_status": "healthy",
        "last_update": "2026-07-01T08:29:22.629732+00:00",
        "latency_ms": 1679.86,
        "source_id": "FRED",
        "source_mode": "official"
      },
      {
        "error": null,
        "health_status": "healthy",
        "last_update": "2026-07-01T08:29:24.309136+00:00",
        "latency_ms": 410.61,
        "source_id": "MOPS",
        "source_mode": "official"
      },
      {
        "error": null,
        "health_status": "healthy",
        "last_update": "2026-07-01T08:29:24.720187+00:00",
        "latency_ms": 646.21,
        "source_id": "SEC_EDGAR",
        "source_mode": "official"
      },
      {
        "error": null,
        "health_status": "healthy",
        "last_update": "2026-07-01T08:29:25.370284+00:00",
        "latency_ms": 3536.19,
        "source_id": "TPEX",
        "source_mode": "official"
      },
      {
        "error": null,
        "health_status": "healthy",
        "last_update": "2026-07-01T08:29:28.911121+00:00",
        "latency_ms": 1397.52,
        "source_id": "TWSE",
        "source_mode": "official"
      }
    ],
    "formal_confidence_modified": false,
    "repository_write_authorized": false
  }
};

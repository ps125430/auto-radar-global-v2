window.AUTO_RADAR_DASHBOARD_DATA = {
  "meta": {
    "generated_at": "2026-06-29T17:17:30.618811+00:00",
    "mode": "知識庫唯讀",
    "repository_status": "通過",
    "validation_errors": 0,
    "validation_warnings": 1,
    "data_gaps": [
      "今日策略",
      "策略信心度",
      "預估有效天數",
      "總經環境",
      "產業狀態",
      "市場情緒",
      "資金流地圖",
      "機會分數"
    ],
    "sources": [
      "每日預測草稿",
      "市場認知草稿",
      "模式候選清冊",
      "驗證案例清冊",
      "證據沙盒",
      "知識圖譜",
      "全域驗證報告"
    ]
  },
  "strategy": {
    "name": null,
    "confidence": null,
    "window": null,
    "why_now": null,
    "status": "草稿",
    "fallback": "等待核准資料建立。"
  },
  "regime": {
    "macro": null,
    "sector": null,
    "micro": null,
    "market_mood": null,
    "dominant_narrative": null,
    "status": "草稿",
    "fallback": "等待核准資料建立。"
  },
  "opportunities": [
    {
      "id": "PC-001",
      "name": "公司公告訊號",
      "opportunity_score": null,
      "why_now": "公司申報與交易所公告案例符合既定標籤規則。",
      "money_flow": null,
      "window": null,
      "crowded": null,
      "risk": "模式候選資料，仍需人工審查。",
      "status": "候選",
      "source_cases": [
        "VC-101",
        "VC-103"
      ],
      "evidence_ids": [
        "EV-101",
        "EV-103"
      ],
      "explainability": {
        "why_score": "目前尚無核准的機會分數，且不會以相似度替代。",
        "evidence": [
          "EV-101",
          "EV-103"
        ],
        "money": "目前尚未連結已驗證的資金流紀錄。",
        "history": [
          "VC-101",
          "VC-103"
        ],
        "risk": "目前仍為候選狀態，不供正式交易使用。"
      }
    },
    {
      "id": "PC-002",
      "name": "總經事件時程",
      "opportunity_score": null,
      "why_now": "總經事件與行事曆案例符合既定標籤規則。",
      "money_flow": null,
      "window": null,
      "crowded": null,
      "risk": "模式候選資料，仍需人工審查。",
      "status": "候選",
      "source_cases": [
        "VC-102",
        "VC-104"
      ],
      "evidence_ids": [
        "EV-102",
        "EV-104"
      ],
      "explainability": {
        "why_score": "目前尚無核准的機會分數，且不會以相似度替代。",
        "evidence": [
          "EV-102",
          "EV-104"
        ],
        "money": "目前尚未連結已驗證的資金流紀錄。",
        "history": [
          "VC-102",
          "VC-104"
        ],
        "risk": "目前仍為候選狀態，不供正式交易使用。"
      }
    },
    {
      "id": "PC-003",
      "name": "人工新聞樣本",
      "opportunity_score": null,
      "why_now": "人工彙整新聞案例符合既定標籤規則。",
      "money_flow": null,
      "window": null,
      "crowded": null,
      "risk": "模式候選資料，仍需人工審查。",
      "status": "候選",
      "source_cases": [
        "VC-105"
      ],
      "evidence_ids": [
        "EV-105"
      ],
      "explainability": {
        "why_score": "目前尚無核准的機會分數，且不會以相似度替代。",
        "evidence": [
          "EV-105"
        ],
        "money": "目前尚未連結已驗證的資金流紀錄。",
        "history": [
          "VC-105"
        ],
        "risk": "目前仍為候選狀態，不供正式交易使用。"
      }
    }
  ],
  "capital_flow": {
    "status": "尚無資料",
    "nodes": [],
    "edges": [],
    "message": "目前尚無已驗證資金流資料。"
  },
  "tactical": {
    "strategy": null,
    "risk": [],
    "window": null,
    "watch": [
      "PC-001 · 等待研究審查",
      "PC-002 · 等待研究審查",
      "PC-003 · 等待研究審查"
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
    "last_run": "2026-06-29T17:17:30.618811+00:00",
    "mode": {
      "label": "Shadow Runtime",
      "status": "Healthy",
      "schema": "PASS",
      "repository": "Read Only",
      "production_authorized": false
    },
    "today": {
      "direction": "公司公告訊號",
      "captain_mission": "以 Shadow 模式觀察 公司公告訊號。",
      "market_story": "今日 Shadow 方向為 公司公告訊號；第一候選為 公司公告訊號，主要風險是 Shadow 輸出僅供觀察，行動前必須人工審查。。",
      "daily_brief": "今日北極星：公司公告訊號。今日航向：以 Shadow 模式觀察 公司公告訊號。。今日 Top3：公司公告訊號, 總經事件時程, 人工新聞樣本。今日風險：Shadow 輸出僅供觀察，行動前必須人工審查。。",
      "risk_summary": [
        "Shadow 輸出僅供觀察，行動前必須人工審查。"
      ],
      "window": "Waiting for today's shadow run...",
      "top3": [
        "公司公告訊號",
        "總經事件時程",
        "人工新聞樣本"
      ],
      "forbidden_zone": [
        "Shadow 輸出不得作為正式交易指令。"
      ]
    },
    "timeline": {
      "yesterday": "Waiting for previous shadow run...",
      "today": "公司公告訊號",
      "tomorrow": "Waiting for next shadow projection..."
    },
    "explain": {
      "chain_id": "EXPLAIN-DASHBOARD-20260629",
      "direction": "公司公告訊號",
      "decision": "NSD-DASHBOARD-20260629",
      "nodes": [
        {
          "node_id": "decision:NSD-DASHBOARD",
          "layer": "decision",
          "reference": "NSD-DASHBOARD-20260629",
          "available": true
        },
        {
          "node_id": "evidence:EV-101",
          "layer": "evidence",
          "reference": "EV-101",
          "available": true
        },
        {
          "node_id": "evidence:EV-103",
          "layer": "evidence",
          "reference": "EV-103",
          "available": true
        },
        {
          "node_id": "evidence:EV-102",
          "layer": "evidence",
          "reference": "EV-102",
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
          "node_id": "pattern:VC-101",
          "layer": "pattern",
          "reference": "VC-101",
          "available": true
        },
        {
          "node_id": "pattern:VC-103",
          "layer": "pattern",
          "reference": "VC-103",
          "available": true
        },
        {
          "node_id": "pattern:VC-102",
          "layer": "pattern",
          "reference": "VC-102",
          "available": true
        },
        {
          "node_id": "pattern:VC-104",
          "layer": "pattern",
          "reference": "VC-104",
          "available": true
        },
        {
          "node_id": "pattern:VC-105",
          "layer": "pattern",
          "reference": "VC-105",
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
          "NSD-DASHBOARD-20260629"
        ],
        "regime": [
          "VC-101",
          "VC-103",
          "VC-102",
          "VC-104",
          "VC-105"
        ],
        "capital_flow": [],
        "evidence": [
          "EV-101",
          "EV-103",
          "EV-102",
          "EV-104",
          "EV-105"
        ],
        "repository": [
          "Dashboard/dashboard-data.js"
        ]
      }
    }
  }
};

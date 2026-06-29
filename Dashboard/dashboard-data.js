window.AUTO_RADAR_DASHBOARD_DATA = {
  "meta": {
    "generated_at": "2026-06-29T01:24:06.913819+00:00",
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
  }
};

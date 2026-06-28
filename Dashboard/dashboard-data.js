window.AUTO_RADAR_DASHBOARD_DATA = {
  "meta": {
    "generated_at": "2026-06-28T16:59:15.888795+00:00",
    "mode": "read_only_repository",
    "repository_status": "PASS",
    "validation_errors": 0,
    "validation_warnings": 1,
    "data_gaps": [
      "Daily strategy",
      "Strategy confidence",
      "Strategy window",
      "Macro regime",
      "Sector regime",
      "Micro regime",
      "Capital flow graph",
      "Opportunity scores"
    ],
    "sources": [
      "Daily Prediction draft",
      "MarketMind draft",
      "Pattern Candidate Registry",
      "Verified Case Registry",
      "Evidence Sandbox",
      "Knowledge Graph",
      "Global Validation Report"
    ]
  },
  "strategy": {
    "name": null,
    "confidence": null,
    "window": null,
    "why_now": null,
    "status": "draft",
    "fallback": "Not provided by an approved Repository record."
  },
  "regime": {
    "macro": null,
    "sector": null,
    "micro": null,
    "market_mood": null,
    "dominant_narrative": null,
    "status": "draft",
    "fallback": "Not provided by an approved Repository record."
  },
  "opportunities": [
    {
      "id": "PC-001",
      "name": "Corporate Disclosure",
      "opportunity_score": null,
      "why_now": "Rule-matched Verified Case tags: filing or exchange.",
      "money_flow": null,
      "window": null,
      "crowded": null,
      "risk": "Pattern Candidate only; human review required.",
      "status": "Candidate",
      "source_cases": [
        "VC-101",
        "VC-103"
      ],
      "evidence_ids": [
        "EV-101",
        "EV-103"
      ],
      "explainability": {
        "why_score": "No approved Opportunity Score exists. Similarity is intentionally not reused.",
        "evidence": [
          "EV-101",
          "EV-103"
        ],
        "money": "No validated money-flow record is linked.",
        "history": [
          "VC-101",
          "VC-103"
        ],
        "risk": "Candidate status; no Production or trading use."
      }
    },
    {
      "id": "PC-002",
      "name": "Macro Calendar",
      "opportunity_score": null,
      "why_now": "Rule-matched Verified Case tags: macro or calendar.",
      "money_flow": null,
      "window": null,
      "crowded": null,
      "risk": "Pattern Candidate only; human review required.",
      "status": "Candidate",
      "source_cases": [
        "VC-102",
        "VC-104"
      ],
      "evidence_ids": [
        "EV-102",
        "EV-104"
      ],
      "explainability": {
        "why_score": "No approved Opportunity Score exists. Similarity is intentionally not reused.",
        "evidence": [
          "EV-102",
          "EV-104"
        ],
        "money": "No validated money-flow record is linked.",
        "history": [
          "VC-102",
          "VC-104"
        ],
        "risk": "Candidate status; no Production or trading use."
      }
    },
    {
      "id": "PC-003",
      "name": "Manual News",
      "opportunity_score": null,
      "why_now": "Rule-matched Verified Case tag: manual.",
      "money_flow": null,
      "window": null,
      "crowded": null,
      "risk": "Pattern Candidate only; human review required.",
      "status": "Candidate",
      "source_cases": [
        "VC-105"
      ],
      "evidence_ids": [
        "EV-105"
      ],
      "explainability": {
        "why_score": "No approved Opportunity Score exists. Similarity is intentionally not reused.",
        "evidence": [
          "EV-105"
        ],
        "money": "No validated money-flow record is linked.",
        "history": [
          "VC-105"
        ],
        "risk": "Candidate status; no Production or trading use."
      }
    }
  ],
  "capital_flow": {
    "status": "not_available",
    "nodes": [],
    "edges": [],
    "message": "No validated capital-flow nodes or edges are stored."
  },
  "tactical": {
    "strategy": null,
    "risk": [],
    "window": null,
    "watch": [
      "PC-001 · research review required",
      "PC-002 · research review required",
      "PC-003 · research review required"
    ],
    "avoid": [],
    "fallback": "Not provided by an approved Repository record."
  },
  "repository": {
    "pattern_candidates": 3,
    "verified_cases": 5,
    "evidence_records": 5,
    "graph_nodes": 0,
    "graph_edges": 0,
    "warnings": [
      "Confidence Repository is not established; confidence_ref is validated for format only when present."
    ]
  }
};

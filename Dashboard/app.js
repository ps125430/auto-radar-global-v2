(() => {
  "use strict";

  const data = window.AUTO_RADAR_DASHBOARD_DATA || {};
  const meta = data.meta || {};
  const strategy = data.strategy || {};
  const regime = data.regime || {};
  const repository = data.repository || {};
  const tactical = data.tactical || {};
  const capitalFlow = data.capital_flow || {};
  const opportunities = Array.isArray(data.opportunities)
    ? data.opportunities.slice(0, 3)
    : [];

  let activeOpportunity = null;
  let activeTab = "why_score";
  let flowMode = "capital";

  const $ = (id) => document.getElementById(id);

  const setText = (id, value, fallback = "—") => {
    const element = $(id);
    if (!element) return;
    if (value === null || value === undefined || value === "") {
      element.textContent = fallback;
      return;
    }
    element.textContent = String(value);
  };

  const escapeHtml = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const listText = (value, fallback) => {
    if (!Array.isArray(value) || value.length === 0) return fallback;
    return value.join(" · ");
  };

  const scoreText = (value) => {
    if (typeof value !== "number" || Number.isNaN(value)) return "—";
    return `${Math.round(value)}`;
  };

  const confidenceText = (value) => {
    if (typeof value !== "number" || Number.isNaN(value)) return "等待分析";
    const percent = value <= 1 ? value * 100 : value;
    return `${Math.round(percent)}%`;
  };

  const windowText = (value) => {
    if (value === null || value === undefined || value === "") {
      return "尚未計算";
    }
    return String(value);
  };

  const dateText = (value) => {
    if (!value) return "等待快照";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value);
    return new Intl.DateTimeFormat("zh-TW", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZone: "Asia/Taipei",
    }).format(parsed);
  };

  const missingEvidence = "等待核准資料";
  const strategyName = strategy.name || "等待今日分析完成";
  const strategyWindow = windowText(strategy.window);
  const strategyWhy =
    strategy.why_now || strategy.fallback || "等待今日分析完成";
  const riskText = listText(tactical.risk, "等待風險分析");
  const opportunityEvidence = opportunities.flatMap((item) =>
    Array.isArray(item.evidence_ids) ? item.evidence_ids : []
  );

  function renderHeader() {
    setText("snapshot-time", dateText(meta.generated_at));
    setText("side-validation", meta.repository_status || "等待驗證");
  }

  function renderNorthStar() {
    setText("north-status", strategy.status || "草稿");
    setText("north-name", strategyName);
    setText("north-confidence", confidenceText(strategy.confidence));
    setText("north-window", strategyWindow);
    setText("north-why", strategyWhy);
    setText(
      "north-evidence",
      opportunityEvidence.length
        ? `關聯證據 ${opportunityEvidence.length} 筆`
        : missingEvidence
    );

    setText("captain-destination", strategyName);
    setText("captain-window", strategyWindow);
    setText("captain-risk", riskText);
    setText(
      "captain-trend",
      strategy.name ? "依核准策略航行" : "等待策略核准"
    );
    setText("captain-why", strategyWhy);
    setText(
      "captain-evidence",
      strategy.name ? "每日預測快照" : missingEvidence
    );

    const avoid = Array.isArray(tactical.avoid) ? tactical.avoid : [];
    setText("avoid-score", avoid.length ? `${avoid.length} 區` : "—");
    setText(
      "avoid-trend",
      avoid.length ? "已建立風險邊界" : "等待風險清單"
    );
    setText(
      "avoid-why",
      avoid.length ? avoid.join(" · ") : "尚無核准的避免布局資料。"
    );
    setText(
      "avoid-evidence",
      avoid.length ? "每日戰術快照" : "風險資料待建立"
    );
  }

  function renderOpportunities() {
    const container = $("opportunity-list");
    if (!container) return;

    if (opportunities.length === 0) {
      container.innerHTML =
        '<div class="opportunity-card"><strong>等待候選資料建立</strong></div>';
      return;
    }

    container.innerHTML = opportunities
      .map((item, index) => {
        const score = scoreText(item.opportunity_score);
        const evidence = listText(item.evidence_ids, "等待證據");
        return `
          <article class="opportunity-card">
            <div class="card-header">
              <span class="rank">${String(index + 1).padStart(2, "0")}</span>
              <span class="status-chip">${escapeHtml(item.status || "候選")}</span>
            </div>
            <div class="opportunity-title">
              <strong>${escapeHtml(item.name || item.id || "未命名候選")}</strong>
              <span>${escapeHtml(item.id || "等待識別碼")}</span>
            </div>
            <div class="opportunity-score-row">
              <div class="score-block">
                <strong>${escapeHtml(score)}</strong>
                <span>${score === "—" ? "尚未評分" : "機會分數"}</span>
              </div>
              <button
                class="explain-button"
                type="button"
                data-opportunity-id="${escapeHtml(item.id)}"
                title="查看決策解釋"
                aria-label="查看 ${escapeHtml(item.name || item.id)} 的決策解釋"
              >
                <i data-lucide="panel-right-open"></i>
              </button>
            </div>
            <div class="opportunity-meta">
              <div><span>觀察窗</span><strong>${escapeHtml(windowText(item.window))}</strong></div>
              <div><span>資金</span><strong>${escapeHtml(item.money_flow || "等待資料")}</strong></div>
              <div><span>風險</span><strong>${escapeHtml(item.risk || "等待評估")}</strong></div>
              <div><span>擁擠度</span><strong>${escapeHtml(item.crowded ?? "等待評估")}</strong></div>
            </div>
            <p class="opportunity-why">${escapeHtml(item.why_now || "等待今日發動原因")}</p>
            <div class="opportunity-evidence">證據 · ${escapeHtml(evidence)}</div>
          </article>
        `;
      })
      .join("");

    container.querySelectorAll("[data-opportunity-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const selected = opportunities.find(
          (item) => item.id === button.dataset.opportunityId
        );
        if (selected) openDrawer(selected);
      });
    });
  }

  const conceptualRoute = [
    { name: "美國", detail: "資金源頭", icon: "landmark" },
    { name: "台灣", detail: "市場接力", icon: "map-pin" },
    { name: "HBM", detail: "記憶體主題", icon: "memory-stick" },
    { name: "散熱", detail: "延伸題材", icon: "fan" },
    { name: "PCB", detail: "供應鏈", icon: "circuit-board" },
  ];

  function validatedRoute() {
    const nodes = Array.isArray(capitalFlow.nodes) ? capitalFlow.nodes : [];
    if (nodes.length === 0) return null;
    return nodes.slice(0, 5).map((node, index) => ({
      name: node.name || node.label || node.id || `節點 ${index + 1}`,
      detail: node.category || node.type || "已驗證節點",
      icon: ["landmark", "map-pin", "memory-stick", "fan", "circuit-board"][
        index
      ],
    }));
  }

  function renderFlow() {
    const route = validatedRoute() || conceptualRoute;
    const container = $("ocean-route");
    if (!container) return;

    container.innerHTML = route
      .map(
        (node) => `
          <div class="flow-node">
            <span class="node-icon"><i data-lucide="${escapeHtml(node.icon)}"></i></span>
            <strong>${escapeHtml(node.name)}</strong>
            <span>${escapeHtml(node.detail)}</span>
          </div>
        `
      )
      .join("");

    if (flowMode === "trace") {
      setText(
        "ocean-status",
        validatedRoute()
          ? "已驗證追溯鏈"
          : "概念追溯鏈 · 尚未建立關聯"
      );
      return;
    }
    setText(
      "ocean-status",
      validatedRoute()
        ? capitalFlow.status || "已驗證洋流"
        : "概念航線 · 尚無已驗證資金流"
    );
  }

  function renderSeaState() {
    const hasFlow = Boolean(validatedRoute());
    const graphNodeCount = Number(repository.graph_nodes || 0);
    const graphEdgeCount = Number(repository.graph_edges || 0);
    const warningCount = Array.isArray(repository.warnings)
      ? repository.warnings.length
      : 0;

    setText("current-score", hasFlow ? `${graphNodeCount} 節點` : "—");
    setText("current-trend", hasFlow ? "已驗證" : "等待驗證");
    setText("current-window", strategyWindow);
    setText(
      "current-why",
      capitalFlow.message || "目前尚無已驗證資金流資料。"
    );
    setText(
      "current-evidence",
      hasFlow ? `圖譜邊 ${graphEdgeCount} 筆` : "知識圖譜待建立"
    );

    setText("tide-score", regime.dominant_narrative || "—");
    setText(
      "tide-trend",
      regime.dominant_narrative ? "敘事已建立" : "等待判讀"
    );
    setText("tide-window", strategyWindow);
    setText(
      "tide-why",
      regime.dominant_narrative
        ? `主導敘事：${regime.dominant_narrative}`
        : "尚無核准的主導敘事資料。"
    );
    setText(
      "tide-evidence",
      regime.dominant_narrative ? "市場認知快照" : missingEvidence
    );

    setText("regime-score", regime.macro || "—");
    setText("regime-trend", regime.status || "等待分析");
    setText(
      "regime-why",
      [regime.macro, regime.sector, regime.micro].filter(Boolean).join(" · ") ||
        "總經、產業與市場情緒仍等待核准資料。"
    );
    setText(
      "regime-evidence",
      regime.macro ? "市場認知快照" : missingEvidence
    );

    setText(
      "health-score",
      meta.repository_status === "通過" ? "通過" : "待檢查"
    );
    setText(
      "health-trend",
      warningCount ? `${warningCount} 項警告` : "資料正常"
    );
    setText(
      "health-why",
      `${Number(meta.validation_errors || 0)} 項錯誤 · ${warningCount} 項警告`
    );
    setText("health-evidence", "全域知識庫驗證報告");
  }

  function renderStory() {
    const story =
      regime.market_mood ||
      regime.dominant_narrative ||
      strategy.why_now ||
      "等待今日市場敘事資料。";
    setText("market-story", story);
    setText(
      "story-evidence",
      story === "等待今日市場敘事資料。"
        ? "證據待建立"
        : "來源：市場認知快照"
    );
  }

  function averageNumber(values) {
    const valid = values.filter(
      (value) => typeof value === "number" && !Number.isNaN(value)
    );
    if (valid.length === 0) return null;
    return valid.reduce((sum, value) => sum + value, 0) / valid.length;
  }

  function renderMoney() {
    const hasFlow = Boolean(validatedRoute());
    const crowdedAverage = averageNumber(
      opportunities.map((item) => item.crowded)
    );
    const scoreAverage = averageNumber(
      opportunities.map((item) => item.opportunity_score)
    );

    setText("smart-score", hasFlow ? `${repository.graph_edges || 0}` : "—");
    setText("smart-trend", hasFlow ? "資金鏈已建立" : "等待驗證");
    setText("smart-window", strategyWindow);
    setText(
      "smart-why",
      hasFlow
        ? "顯示知識圖譜中的已驗證資金關聯。"
        : "目前沒有可用的已驗證資金足跡。"
    );
    setText("smart-evidence", hasFlow ? "知識圖譜" : "圖譜資料待建立");

    setText(
      "density-score",
      crowdedAverage === null ? "—" : `${Math.round(crowdedAverage)}`
    );
    setText(
      "density-trend",
      crowdedAverage === null ? "等待評估" : "已建立密度資料"
    );
    setText("density-window", strategyWindow);
    setText(
      "density-why",
      crowdedAverage === null
        ? "前三候選尚無核准的籌碼擁擠度。"
        : "依前三候選的核准擁擠度平均呈現。"
    );
    setText(
      "density-evidence",
      crowdedAverage === null ? missingEvidence : "機會候選快照"
    );

    setText(
      "energy-score",
      scoreAverage === null ? "—" : `${Math.round(scoreAverage)}`
    );
    setText(
      "energy-trend",
      scoreAverage === null ? "等待分析" : "候選能量已建立"
    );
    setText("energy-window", strategyWindow);
    setText(
      "energy-why",
      scoreAverage === null
        ? "目前沒有核准的機會分數可計算市場能量。"
        : "依核准機會分數的平均值呈現。"
    );
    setText(
      "energy-evidence",
      scoreAverage === null ? missingEvidence : "機會候選快照"
    );

    setText("velocity-score", "—");
    setText("velocity-trend", "等待分析");
    setText("velocity-window", strategyWindow);
    setText(
      "velocity-why",
      "尚無核准的資金傳導時間與速度資料。"
    );
    setText("velocity-evidence", "結果視窗資料待建立");
  }

  function renderKnowledge() {
    const patterns = Number(repository.pattern_candidates || 0);
    const cases = Number(repository.verified_cases || 0);
    const evidence = Number(repository.evidence_records || 0);
    const gaps = Array.isArray(meta.data_gaps) ? meta.data_gaps : [];

    setText(
      "repository-score",
      meta.repository_status === "通過" ? "通過" : "待檢查"
    );
    setText(
      "repository-trend",
      gaps.length ? `${gaps.length} 項缺口` : "資料完整"
    );
    setText("count-patterns", patterns);
    setText("count-cases", cases);
    setText("count-evidence", evidence);
    setText(
      "repository-why",
      gaps.length ? gaps.slice(0, 3).join(" · ") : "目前沒有已知資料缺口。"
    );
    setText("repository-evidence", "全域知識庫驗證報告");

    setText("learning-score", cases ? `${cases} 案例` : "—");
    setText(
      "learning-learned",
      cases ? `可追溯案例 ${cases} 筆` : "等待案例"
    );
    setText("learning-corrected", "等待檢討紀錄");
    setText(
      "learning-added",
      patterns ? `模式候選 ${patterns} 筆` : "等待候選"
    );
    setText("learning-evidence", "案例與模式候選清冊");

    setText("evolution-score", patterns ? `${patterns} 候選` : "—");
    setText("evolution-growing", patterns ? `${patterns}` : "—");
    setText("evolution-stable", "—");
    setText("evolution-weakening", "—");
    setText("evolution-deprecated", "—");
    setText("evolution-evidence", "等待完整生命週期資料");

    setText("review-score", "—");
    setText("review-trend", "等待檢討資料");
    setText("review-why", "尚無核准的每日檢討紀錄。");
    setText("review-evidence", "檢討清冊待連結");
  }

  function renderDrawerContent() {
    if (!activeOpportunity) return;
    const explainability = activeOpportunity.explainability || {};
    const value = explainability[activeTab];
    const content = $("drawer-content");
    if (!content) return;

    if (Array.isArray(value)) {
      content.innerHTML = value.length
        ? `<ul>${value
            .map((item) => `<li>${escapeHtml(item)}</li>`)
            .join("")}</ul>`
        : "<p>等待資料建立。</p>";
      return;
    }
    content.innerHTML = `<p>${escapeHtml(value || "等待資料建立。")}</p>`;
  }

  function openDrawer(item) {
    activeOpportunity = item;
    activeTab = "why_score";
    setText("drawer-title", `${item.id || ""} · ${item.name || "未命名候選"}`);
    setText("drawer-score", scoreText(item.opportunity_score));

    document.querySelectorAll("[data-tab]").forEach((tab) => {
      const selected = tab.dataset.tab === activeTab;
      tab.classList.toggle("active", selected);
      tab.setAttribute("aria-selected", String(selected));
    });

    renderDrawerContent();
    $("drawer-backdrop").hidden = false;
    $("explain-drawer").classList.add("open");
    $("explain-drawer").setAttribute("aria-hidden", "false");
    document.body.classList.add("drawer-open");
    $("drawer-close").focus();
  }

  function closeDrawer() {
    $("explain-drawer").classList.remove("open");
    $("explain-drawer").setAttribute("aria-hidden", "true");
    $("drawer-backdrop").hidden = true;
    document.body.classList.remove("drawer-open");
  }

  function bindEvents() {
    $("refresh-button")?.addEventListener("click", () => window.location.reload());
    $("drawer-close")?.addEventListener("click", closeDrawer);
    $("drawer-backdrop")?.addEventListener("click", closeDrawer);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeDrawer();
    });

    document.querySelectorAll("[data-tab]").forEach((tab) => {
      tab.addEventListener("click", () => {
        activeTab = tab.dataset.tab;
        document.querySelectorAll("[data-tab]").forEach((candidate) => {
          const selected = candidate === tab;
          candidate.classList.toggle("active", selected);
          candidate.setAttribute("aria-selected", String(selected));
        });
        renderDrawerContent();
      });
    });

    document.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        flowMode = button.dataset.flowMode;
        document.querySelectorAll("[data-flow-mode]").forEach((candidate) => {
          candidate.classList.toggle("active", candidate === button);
        });
        renderFlow();
        createIcons();
      });
    });

    const sections = document.querySelectorAll("main section[id]");
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            document.querySelectorAll(".nav-item").forEach((item) => {
              item.classList.toggle(
                "active",
                item.getAttribute("href") === `#${entry.target.id}`
              );
            });
          });
        },
        { rootMargin: "-20% 0px -65% 0px" }
      );
      sections.forEach((section) => observer.observe(section));
    }
  }

  function createIcons() {
    if (window.lucide?.createIcons) {
      window.lucide.createIcons({
        attrs: {
          "stroke-width": 1.8,
          "aria-hidden": "true",
        },
      });
    }
  }

  function render() {
    renderHeader();
    renderNorthStar();
    renderOpportunities();
    renderFlow();
    renderSeaState();
    renderStory();
    renderMoney();
    renderKnowledge();
    bindEvents();
    createIcons();
  }

  render();
})();

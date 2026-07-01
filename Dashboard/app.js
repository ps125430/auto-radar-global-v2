(() => {
  "use strict";

  const data = window.AUTO_RADAR_DASHBOARD_DATA || {};
  const meta = data.meta || {};
  const strategy = data.strategy || {};
  const regime = data.regime || {};
  const repository = data.repository || {};
  const tactical = data.tactical || {};
  const capitalFlow = data.capital_flow || {};
  const shadowRuntime = data.shadow_runtime || {};
  const shadowToday = shadowRuntime.today || {};
  const shadowMode = shadowRuntime.mode || {};
  const shadowTimeline = shadowRuntime.timeline || {};
  const shadowExplain = shadowRuntime.explain || {};
  const livingOcean = data.living_ocean || {};
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

  const waitingShadow =
    shadowRuntime.waiting_message || "Waiting for today's shadow run...";
  const missingEvidence = waitingShadow;
  const strategyName =
    shadowToday.direction || strategy.name || waitingShadow;
  const strategyWindow = windowText(shadowToday.window || strategy.window);
  const strategyWhy =
    shadowToday.why_now ||
    shadowToday.market_story ||
    strategy.why_now ||
    strategy.fallback ||
    waitingShadow;
  const riskText = listText(
    shadowToday.risk_summary || tactical.risk,
    waitingShadow
  );
  const opportunityEvidence = opportunities.flatMap((item) =>
    Array.isArray(item.evidence_ids) ? item.evidence_ids : []
  );

  function renderHeader() {
    setText("snapshot-time", dateText(shadowRuntime.last_run || meta.generated_at));
    setText("side-validation", shadowMode.status || meta.repository_status || "Waiting");
  }

  function renderNorthStar() {
    setText("north-status", shadowMode.label || strategy.status || "Shadow Runtime");
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
      shadowToday.captain_mission ? "Shadow Runtime 輸出" : waitingShadow
    );
    setText("captain-why", shadowToday.captain_mission || strategyWhy);
    setText(
      "captain-evidence",
      shadowExplain.chain_id || missingEvidence
    );

    const avoid = Array.isArray(shadowToday.forbidden_zone)
      ? shadowToday.forbidden_zone
      : Array.isArray(tactical.avoid)
        ? tactical.avoid
        : [];
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
      avoid.length ? "Shadow Runtime Risk Boundary" : waitingShadow
    );

    setText("shadow-last-run", dateText(shadowRuntime.last_run));
    setText("shadow-status", shadowMode.status || "Waiting");
    setText("shadow-schema", shadowMode.schema || "WAITING");
    setText("shadow-repository", shadowMode.repository || "Read Only");
    setText("timeline-yesterday", shadowTimeline.yesterday || waitingShadow);
    setText("timeline-today", shadowTimeline.today || waitingShadow);
    setText("timeline-tomorrow", shadowTimeline.tomorrow || waitingShadow);
    setText("daily-brief", shadowToday.daily_brief || waitingShadow);
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
              <span>${score === "—" ? "尚未評分" : "Shadow 顯示分數"}</span>
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
    const graphNodeCount = Array.isArray(capitalFlow.nodes)
      ? capitalFlow.nodes.length
      : 0;
    const graphEdgeCount = Array.isArray(capitalFlow.edges)
      ? capitalFlow.edges.length
      : 0;
    const warningCount = Array.isArray(repository.warnings)
      ? repository.warnings.length
      : 0;

    setText("current-score", hasFlow ? `${graphNodeCount} 節點` : "—");
    setText("current-trend", hasFlow ? "Shadow 輸入" : "等待驗證");
    setText("current-window", strategyWindow);
    setText(
      "current-why",
      hasFlow
        ? "顯示半真實 Shadow 輸入的資金傳導路徑。"
        : capitalFlow.message || "目前尚無已驗證資金流資料。"
    );
    setText(
      "current-evidence",
      hasFlow ? `Shadow 路徑 ${graphEdgeCount} 段` : "知識圖譜待建立"
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

    const oceanScore =
      typeof livingOcean.health_score === "number"
        ? `${Math.round(livingOcean.health_score)}%`
        : null;
    setText(
      "health-score",
      oceanScore || (meta.repository_status === "通過" ? "通過" : "待檢查")
    );
    setText(
      "health-trend",
      livingOcean.overall_status
        ? oceanHealthLabel(livingOcean.overall_status)
        : warningCount
          ? `${warningCount} 項警告`
          : "資料正常"
    );
    setText(
      "health-why",
      typeof livingOcean.evidence_coverage === "number"
        ? `Evidence 覆蓋率 ${livingOcean.evidence_coverage}% · 正式信心度未修改`
        : `${Number(meta.validation_errors || 0)} 項錯誤 · ${warningCount} 項警告`
    );
    setText(
      "health-evidence",
      livingOcean.snapshot_version
        ? `Global Snapshot ${livingOcean.snapshot_version}`
        : "全域知識庫驗證報告"
    );
    renderLivingOcean();
  }

  function oceanHealthLabel(status) {
    return {
      healthy: "健康",
      warning: "警告",
      degraded: "降級",
      unavailable: "中斷",
      waiting: "等待資料",
    }[status] || "狀態未知";
  }

  function renderLivingOcean() {
    setText(
      "ocean-health-status",
      oceanHealthLabel(livingOcean.overall_status)
    );
    setText(
      "ocean-snapshot-time",
      livingOcean.snapshot_version
        ? `${livingOcean.snapshot_version} · ${dateText(livingOcean.generated_at)}`
        : "尚無快照"
    );
    setText(
      "ocean-evidence-coverage",
      typeof livingOcean.evidence_coverage === "number"
        ? `Evidence 覆蓋率 ${livingOcean.evidence_coverage}%`
        : "Evidence 等待建立"
    );

    const container = $("source-health-grid");
    if (!container) return;
    const sources = Array.isArray(livingOcean.sources)
      ? livingOcean.sources
      : [];
    if (sources.length === 0) {
      container.innerHTML = "<p>等待今日 Shadow Snapshot。</p>";
      return;
    }
    const displayNames = {
      TWSE: "TWSE",
      TPEX: "TPEx",
      MOPS: "MOPS",
      US_MARKET: "美國市場",
      MACRO: "總經",
      ETF: "ETF",
      NEWS: "新聞",
      FRED: "FRED",
      SEC_EDGAR: "SEC",
    };
    container.innerHTML = sources
      .map(
        (source) => `
          <div class="source-health-item">
            <span class="health-dot health-${escapeHtml(source.health_status)}"></span>
            <div>
              <strong>${escapeHtml(displayNames[source.source_id] || source.source_id)}</strong>
              <span>${escapeHtml(oceanHealthLabel(source.health_status))} · ${
                typeof source.latency_ms === "number"
                  ? `${Math.round(source.latency_ms)} ms`
                  : `Evidence ${Number(source.evidence_count || 0)}`
              }</span>
            </div>
          </div>
        `
      )
      .join("");
  }

  function renderStory() {
    const story =
      shadowToday.market_story ||
      regime.market_mood ||
      regime.dominant_narrative ||
      strategy.why_now ||
      waitingShadow;
    setText("market-story", story);
    setText(
      "story-evidence",
      shadowExplain.chain_id || "Runtime Explain Chain"
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
    const leadDisplayScore = opportunities[0]?.opportunity_score;

    setText("smart-score", hasFlow ? `${capitalFlow.edges.length}` : "—");
    setText("smart-trend", hasFlow ? "Shadow 路徑" : "等待驗證");
    setText("smart-window", strategyWindow);
    setText(
      "smart-why",
      hasFlow
        ? "顯示半真實 Shadow 輸入的資金關聯，不代表已驗證市場事實。"
        : "目前沒有可用的已驗證資金足跡。"
    );
    setText("smart-evidence", hasFlow ? "Shadow Input Pack" : "圖譜資料待建立");

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
      typeof leadDisplayScore === "number" ? `${Math.round(leadDisplayScore)}` : "—"
    );
    setText(
      "energy-trend",
      typeof leadDisplayScore === "number" ? "Shadow 輸入值" : "等待分析"
    );
    setText("energy-window", strategyWindow);
    setText(
      "energy-why",
      typeof leadDisplayScore !== "number"
        ? "目前沒有核准的機會分數可計算市場能量。"
        : "顯示第一候選的半真實測試輸入值，不是 Runtime 計算結果。"
    );
    setText(
      "energy-evidence",
      typeof leadDisplayScore !== "number" ? missingEvidence : "Shadow Input Pack"
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

  function renderShadowExplainContent() {
    const content = $("drawer-content");
    if (!content) return;
    const layers = shadowExplain.layers || {};
    const rows = [
      ["Direction", shadowExplain.direction || waitingShadow],
      ["Decision", shadowExplain.decision || waitingShadow],
      ["Regime", listText(layers.regime, waitingShadow)],
      ["Capital Flow", listText(layers.capital_flow, waitingShadow)],
      ["Evidence", listText(layers.evidence, waitingShadow)],
      ["Repository", listText(layers.repository, waitingShadow)],
    ];
    content.innerHTML = `
      <ol class="explain-chain-list">
        ${rows
          .map(
            ([label, value]) => `
              <li>
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(value)}</strong>
              </li>
            `
          )
          .join("")}
      </ol>
    `;
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

  function openShadowExplain() {
    activeOpportunity = null;
    setText("drawer-title", "Today's Direction · Runtime Explain Chain");
    setText("drawer-score", shadowMode.status || "Shadow");

    document.querySelectorAll("[data-tab]").forEach((tab) => {
      tab.classList.remove("active");
      tab.setAttribute("aria-selected", "false");
    });

    renderShadowExplainContent();
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
    $("direction-explain-button")?.addEventListener("click", openShadowExplain);
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

(() => {
  "use strict";

  const data = window.AUTO_RADAR_DASHBOARD_DATA;
  if (!data) {
    document.body.innerHTML = "<main><p>儀表板資料目前無法載入。</p></main>";
    return;
  }

  const unavailable = "等待資料建立";
  let selectedOpportunity = null;
  let activeTab = "why_score";
  let flowMode = "capital";

  const byId = (id) => document.getElementById(id);
  const text = (id, value) => {
    const node = byId(id);
    if (!node) return;
    const missing = value === null || value === undefined || value === "";
    node.textContent = missing ? unavailable : String(value);
    node.classList.toggle("unavailable", missing);
  };
  const esc = (value) =>
    String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  const displayScore = (value) =>
    typeof value === "number" ? Math.round(value) : "—";
  const displayList = (values, fallback = unavailable) =>
    Array.isArray(values) && values.length ? values.join(" · ") : fallback;
  const statusText = (value) => {
    const statuses = {
      PASS: "通過",
      DRAFT: "草稿",
      draft: "草稿",
      Candidate: "候選",
      candidate: "候選",
      UNKNOWN: "未知",
      unknown: "未知",
    };
    return statuses[value] || value || "未知";
  };

  function renderHeader() {
    const generated = new Date(data.meta.generated_at);
    text(
      "snapshot-time",
      Number.isNaN(generated.getTime())
        ? data.meta.generated_at
        : generated.toLocaleString("zh-TW", {
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
          })
    );
    text("side-validation", statusText(data.meta.repository_status));
  }

  function renderTactical() {
    text("tactical-strategy", data.tactical.strategy || "等待今日分析完成");
    text("tactical-window", data.tactical.window || "尚未計算");
    text("tactical-risk", displayList(data.tactical.risk, "等待風險分析"));
    text("tactical-watch", displayList(data.tactical.watch));
    text("tactical-avoid", displayList(data.tactical.avoid, "等待避免布局清單"));
  }

  function renderStrategy() {
    text("strategy-name", data.strategy.name || "等待今日分析完成");
    text(
      "strategy-confidence",
      typeof data.strategy.confidence === "number"
        ? `${data.strategy.confidence}%`
        : "等待分析"
    );
    text("strategy-window", data.strategy.window || "尚未計算");
    text("strategy-why", data.strategy.why_now || "等待今日分析完成");
    text("strategy-status", statusText(data.strategy.status));
  }

  function renderRegime() {
    text("regime-macro", data.regime.macro || "等待總經分析");
    text("regime-sector", data.regime.sector || "等待產業分析");
    text("regime-micro", data.regime.micro || "等待市場情緒分析");
    text("regime-status", statusText(data.regime.status));
  }

  function renderHealth() {
    text("health-badge", statusText(data.meta.repository_status));
    text("count-patterns", data.repository.pattern_candidates);
    text("count-cases", data.repository.verified_cases);
    text("count-evidence", data.repository.evidence_records);
    const gapCount = data.meta.data_gaps.length;
    text("gap-count", `${gapCount} 項缺口`);
    const tracked = 8;
    const readiness = Math.max(0, Math.round(((tracked - gapCount) / tracked) * 100));
    byId("readiness-bar").style.width = `${readiness}%`;
    text(
      "gap-note",
      gapCount
        ? data.meta.data_gaps.slice(0, 3).join(" · ")
        : "所有追蹤資料均已建立。"
    );
  }

  function renderOpportunities() {
    const container = byId("opportunity-list");
    const opportunities = [...data.opportunities].sort((a, b) => {
      const aScore = typeof a.opportunity_score === "number" ? a.opportunity_score : -1;
      const bScore = typeof b.opportunity_score === "number" ? b.opportunity_score : -1;
      return bScore - aScore || a.id.localeCompare(b.id);
    });

    container.innerHTML = opportunities
      .slice(0, 3)
      .map(
        (item, index) => `
          <article class="opportunity-card">
            <span class="rank">${String(index + 1).padStart(2, "0")}</span>
            <div class="opportunity-title">
              <strong>${esc(item.name)}</strong>
              <span>${esc(item.id)} · ${esc(statusText(item.status))}</span>
            </div>
            <div class="score-block">
              <strong>${displayScore(item.opportunity_score)}</strong>
              <span>${typeof item.opportunity_score === "number" ? "機會分數" : "尚未評分"}</span>
            </div>
            <div class="opportunity-meta">
              <div><span>預估有效天數</span><strong>${esc(item.window || "尚未計算")}</strong></div>
              <div><span>籌碼擁擠度</span><strong>${esc(item.crowded || "尚未評估")}</strong></div>
              <div><span>資金流</span><strong>${esc(item.money_flow || "等待資金流資料")}</strong></div>
              <div><span>風險</span><strong>${esc(item.risk || "等待風險分析")}</strong></div>
            </div>
            <button class="explain-button" type="button" data-explain="${esc(item.id)}" title="查看決策解釋" aria-label="查看 ${esc(item.name)} 的決策解釋">
              <i data-lucide="panel-right-open"></i>
            </button>
          </article>
        `
      )
      .join("");

    container.querySelectorAll("[data-explain]").forEach((button) => {
      button.addEventListener("click", () => openDrawer(button.dataset.explain));
    });
  }

  function renderFlow() {
    const container = byId("flow-view");
    if (flowMode === "trace") {
      container.innerHTML = `
        <div class="trace-grid">
          ${data.opportunities
            .map(
              (item) => `
                <div class="trace-row">
                  <strong>${esc(item.id)}</strong>
                  <span class="trace-arrow">→</span>
                  <div class="trace-links">
                    <span>驗證案例 · ${esc(displayList(item.source_cases))}</span>
                    <span>證據 · ${esc(displayList(item.evidence_ids))}</span>
                  </div>
                </div>
              `
            )
            .join("")}
        </div>
      `;
      return;
    }

    const stages = [
      ["上游龍頭", "等待已驗證資料"],
      ["中游接棒", "等待已驗證資料"],
      ["台股主題", "等待已驗證資料"],
      ["延伸題材", "等待已驗證資料"],
    ];
    container.innerHTML = `
      <div class="capital-chain">
        ${stages
          .map(
            ([label, value]) => `
              <div class="flow-node">
                <div><span>${esc(label)}</span><strong>${esc(value)}</strong></div>
                <em>尚未建立關聯</em>
              </div>
            `
          )
          .join("")}
      </div>
      <div class="flow-empty">${esc(data.capital_flow.message || "目前尚無已驗證資金流資料。")}</div>
    `;
  }

  function tabContent(item, tab) {
    const value = item.explainability[tab];
    if (Array.isArray(value)) {
      return value.length
        ? `<ul>${value.map((entry) => `<li>${esc(entry)}</li>`).join("")}</ul>`
        : `<p class="unavailable">${unavailable}</p>`;
    }
    return `<p>${esc(value || unavailable)}</p>`;
  }

  function renderDrawer() {
    if (!selectedOpportunity) return;
    text("drawer-title", `${selectedOpportunity.id} · ${selectedOpportunity.name}`);
    text("drawer-score", displayScore(selectedOpportunity.opportunity_score));
    byId("drawer-content").innerHTML = tabContent(selectedOpportunity, activeTab);
    document.querySelectorAll(".tab").forEach((tab) => {
      const active = tab.dataset.tab === activeTab;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", String(active));
    });
  }

  function openDrawer(id) {
    selectedOpportunity = data.opportunities.find((item) => item.id === id);
    if (!selectedOpportunity) return;
    activeTab = "why_score";
    renderDrawer();
    byId("drawer-backdrop").hidden = false;
    byId("explain-drawer").classList.add("open");
    byId("explain-drawer").setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeDrawer() {
    byId("explain-drawer").classList.remove("open");
    byId("explain-drawer").setAttribute("aria-hidden", "true");
    byId("drawer-backdrop").hidden = true;
    document.body.style.overflow = "";
  }

  function bindEvents() {
    byId("refresh-button").addEventListener("click", () => window.location.reload());
    byId("drawer-close").addEventListener("click", closeDrawer);
    byId("drawer-backdrop").addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeDrawer();
    });
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        activeTab = tab.dataset.tab;
        renderDrawer();
      });
    });
    document.querySelectorAll("[data-flow-mode]").forEach((button) => {
      button.addEventListener("click", () => {
        flowMode = button.dataset.flowMode;
        document.querySelectorAll("[data-flow-mode]").forEach((item) => {
          item.classList.toggle("active", item === button);
        });
        renderFlow();
      });
    });
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.addEventListener("click", () => {
        document.querySelectorAll(".nav-item").forEach((nav) => nav.classList.remove("active"));
        item.classList.add("active");
      });
    });
  }

  function render() {
    renderHeader();
    renderTactical();
    renderStrategy();
    renderRegime();
    renderHealth();
    renderOpportunities();
    renderFlow();
    bindEvents();
    if (window.lucide) window.lucide.createIcons();
  }

  render();
})();

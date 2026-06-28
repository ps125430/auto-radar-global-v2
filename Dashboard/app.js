(() => {
  "use strict";

  const data = window.AUTO_RADAR_DASHBOARD_DATA;
  if (!data) {
    document.body.innerHTML = "<main><p>Dashboard data is unavailable.</p></main>";
    return;
  }

  const unavailable = "Not available";
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
    text("side-validation", data.meta.repository_status);
  }

  function renderTactical() {
    text("tactical-strategy", data.tactical.strategy);
    text("tactical-window", data.tactical.window);
    text("tactical-risk", displayList(data.tactical.risk));
    text("tactical-watch", displayList(data.tactical.watch));
    text("tactical-avoid", displayList(data.tactical.avoid));
  }

  function renderStrategy() {
    text("strategy-name", data.strategy.name);
    text(
      "strategy-confidence",
      typeof data.strategy.confidence === "number"
        ? `${data.strategy.confidence}%`
        : null
    );
    text("strategy-window", data.strategy.window);
    text("strategy-why", data.strategy.why_now);
    text("strategy-status", data.strategy.status);
  }

  function renderRegime() {
    text("regime-macro", data.regime.macro);
    text("regime-sector", data.regime.sector);
    text("regime-micro", data.regime.micro);
    text("regime-status", data.regime.status);
  }

  function renderHealth() {
    text("health-badge", data.meta.repository_status);
    text("count-patterns", data.repository.pattern_candidates);
    text("count-cases", data.repository.verified_cases);
    text("count-evidence", data.repository.evidence_records);
    const gapCount = data.meta.data_gaps.length;
    text("gap-count", `${gapCount} gap${gapCount === 1 ? "" : "s"}`);
    const tracked = 8;
    const readiness = Math.max(0, Math.round(((tracked - gapCount) / tracked) * 100));
    byId("readiness-bar").style.width = `${readiness}%`;
    text(
      "gap-note",
      gapCount
        ? data.meta.data_gaps.slice(0, 3).join(" · ")
        : "All tracked inputs are available."
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
              <span>${esc(item.id)} · ${esc(item.status || "Unknown")}</span>
            </div>
            <div class="score-block">
              <strong>${displayScore(item.opportunity_score)}</strong>
              <span>${typeof item.opportunity_score === "number" ? "Score" : "Not scored"}</span>
            </div>
            <div class="opportunity-meta">
              <div><span>Window</span><strong>${esc(item.window || unavailable)}</strong></div>
              <div><span>Crowded</span><strong>${esc(item.crowded || unavailable)}</strong></div>
              <div><span>Money Flow</span><strong>${esc(item.money_flow || unavailable)}</strong></div>
              <div><span>Risk</span><strong>${esc(item.risk || unavailable)}</strong></div>
            </div>
            <button class="explain-button" type="button" data-explain="${esc(item.id)}" title="Open explainability" aria-label="Explain ${esc(item.name)}">
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
                    <span>Cases · ${esc(displayList(item.source_cases))}</span>
                    <span>Evidence · ${esc(displayList(item.evidence_ids))}</span>
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
      ["Leader", "Awaiting validated node"],
      ["Follower", "Awaiting validated node"],
      ["Taiwan Theme", "Awaiting validated node"],
      ["Sub Theme", "Awaiting validated node"],
    ];
    container.innerHTML = `
      <div class="capital-chain">
        ${stages
          .map(
            ([label, value]) => `
              <div class="flow-node">
                <div><span>${esc(label)}</span><strong>${esc(value)}</strong></div>
                <em>Unlinked</em>
              </div>
            `
          )
          .join("")}
      </div>
      <div class="flow-empty">${esc(data.capital_flow.message || "Capital flow is unavailable.")}</div>
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

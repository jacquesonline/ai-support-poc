const state = {
  brief: null,
  scenarios: [],
  selectedId: null,
  cases: new Map(),
  improvement: null,
  harvey: null,
};

const el = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const titleCase = (value) => String(value ?? "")
  .replaceAll("_", " ")
  .replace(/\b\w/g, (letter) => letter.toUpperCase());

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || `Request failed with ${response.status}`);
  }
  return body;
}

function showToast(message) {
  const toast = el("toast");
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 3200);
}

function renderBrief() {
  const brief = state.brief;
  el("hypothesis").textContent = brief.hypothesis;
  el("outcome-grid").innerHTML = brief.outcomes.map((outcome) => `
    <article class="outcome-card">
      <strong>${escapeHtml(outcome.target)}</strong>
      <h3>${escapeHtml(outcome.name)}</h3>
      <p>${escapeHtml(outcome.measure)}</p>
    </article>
  `).join("");
  el("business-questions").innerHTML = brief.business_questions
    .map((question) => `<li>${escapeHtml(question)}</li>`)
    .join("");
  el("stop-criteria").innerHTML = brief.stop_criteria
    .map((criterion) => `<li>${escapeHtml(criterion)}</li>`)
    .join("");
}

function renderHarveyOverview(overview) {
  state.harvey = overview;
  el("harvey-context").textContent = `${overview.public_context.statement} ${overview.public_context.boundary}`;
  el("harvey-users").innerHTML = overview.users.map((item) => `
    <article><strong>${escapeHtml(item.role)}</strong><p>${escapeHtml(item.outcome)}</p></article>
  `).join("");
  el("harvey-cases").innerHTML = overview.use_cases.map((item) => `
    <article class="harvey-case">
      <div><span>${escapeHtml(item.harvey_surfaces)}</span><h3>${escapeHtml(item.name)}</h3></div>
      <p><strong>Need:</strong> ${escapeHtml(item.need)}</p>
      <p><strong>Better outcome:</strong> ${escapeHtml(item.better_outcome)}</p>
      <p class="not-claimed"><strong>Boundary:</strong> ${escapeHtml(item.not_claimed)}</p>
      <code>${escapeHtml(item.prompt_path)} · ${escapeHtml(item.skill_path)}</code>
    </article>
  `).join("");
  el("harvey-decisions").innerHTML = overview.decision_model.map((item) => `<div class="reuse-item"><small>${escapeHtml(item)}</small></div>`).join("");
  el("harvey-sources").innerHTML = overview.public_context.sources.map((item) => `
    <a class="reuse-item source-link" href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer"><strong>${escapeHtml(item.label)} ↗</strong><small>${escapeHtml(item.supports)}</small></a>
  `).join("");
  if (overview.last_run) renderHarveyRun(overview.last_run);
}

function renderHarveyRun(run) {
  el("harvey-results").hidden = false;
  const metrics = [
    { value: `${run.readiness.use_cases_ready_for_controlled_pilot}/${run.readiness.total_use_cases}`, label: "pilot designs complete" },
    { value: run.readiness.source_contracts_required, label: "source boundaries required" },
    { value: run.readiness.lawyer_review_gates, label: "lawyer review gates" },
    { value: run.readiness.autonomous_legal_actions, label: "autonomous legal actions" },
    { value: "Not yet", label: "real outcome evidence" },
    { value: "Not yet", label: "financial value established" },
  ];
  el("harvey-metrics").innerHTML = metrics.map((item) => `<article><strong>${escapeHtml(item.value)}</strong><small>${escapeHtml(item.label)}</small></article>`).join("");
  el("court-boundary").textContent = run.court_outcome_boundary;
  el("economics-boundary").textContent = `${run.evidence_boundary} ${run.economics.status}`;
}

async function runHarveyEvaluation() {
  const button = el("run-harvey");
  button.disabled = true;
  button.textContent = "Checking four pilot designs…";
  try {
    const run = await fetchJson("/harvey/evaluate", { method: "POST" });
    renderHarveyRun(run);
    showToast(`Harvey readiness review complete: ${run.readiness.use_cases_ready_for_controlled_pilot}/${run.readiness.total_use_cases} use cases have a controlled pilot design.`);
  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Assess readiness for a controlled pilot";
  }
}

function renderScenarios() {
  el("scenario-list").innerHTML = state.scenarios.map((scenario, index) => {
    const active = scenario.id === state.selectedId ? " active" : "";
    const recorded = state.cases.get(scenario.id);
    const result = recorded ? ` · ${titleCase(recorded.state)}` : "";
    return `
      <button class="scenario-button${active}" type="button" data-scenario-id="${escapeHtml(scenario.id)}" role="listitem">
        <span class="scenario-number">${String(index + 1).padStart(2, "0")}</span>
        <span>
          <strong>${escapeHtml(scenario.name)}</strong>
          <small>${escapeHtml(scenario.description)}${escapeHtml(result)}</small>
        </span>
      </button>
    `;
  }).join("");

  document.querySelectorAll("[data-scenario-id]").forEach((button) => {
    button.addEventListener("click", () => selectScenario(button.dataset.scenarioId));
  });
}

function selectScenario(id) {
  state.selectedId = id;
  const scenario = state.scenarios.find((item) => item.id === id);
  el("selected-name").textContent = scenario?.name || "Choose a scenario";
  el("run-case").disabled = !scenario;
  el("run-case").textContent = state.cases.has(id) ? "Run again" : "Investigate request";
  renderScenarios();
  if (state.cases.has(id)) {
    renderCase(state.cases.get(id));
  } else {
    el("case-empty").hidden = false;
    el("case-view").hidden = true;
  }
}

function statusCopy(caseRecord) {
  const messages = {
    awaiting_approval: "Evidence and policy checks passed. A named human decision is required before execution.",
    blocked: "A deterministic control has blocked execution. Approval cannot override this boundary.",
    needs_clarification: "The request is incomplete. The workflow stopped before a model call and raised a question.",
    rejected: "The named reviewer rejected the proposal. No business action was executed.",
    executed: "Named approval recorded. The permitted legal-support action and professional reply were added to the audit trail.",
  };
  return messages[caseRecord.state] || titleCase(caseRecord.state);
}

function proposalMarkup(caseRecord) {
  const decision = caseRecord.decision;
  if (!decision) {
    return `
      <div class="proposal-block">
        <span>Proposal</span>
        <p>No proposal was generated. Evidence was insufficient or conflicting.</p>
      </div>
      <div class="proposal-block">
        <span>Next move</span>
        <p>Resolve the visible question or exception, then start a new controlled run.</p>
      </div>
    `;
  }
  const action = decision.proposed_action;
  return `
    <div class="proposal-block">
      <span>Summary</span>
      <p>${escapeHtml(decision.summary)}</p>
    </div>
    <div class="proposal-block">
      <span>Reasoning</span>
      <p>${escapeHtml(decision.reasoning)}</p>
    </div>
    <div class="proposal-block">
      <span>Action</span>
      <p>${escapeHtml(titleCase(action.action_type))} · ${escapeHtml(action.reference_id || "No matter reference")} · ${escapeHtml(action.target_system)}</p>
    </div>
    <div class="proposal-block">
      <span>Control code</span>
      <p>${escapeHtml(action.resolution_code)}</p>
    </div>
    <div class="proposal-block">
      <span>Draft reply</span>
      <p>${escapeHtml(action.professional_message)}</p>
    </div>
  `;
}

function evidenceMarkup(items) {
  return items.map((item) => `
    <div class="stack-item ${escapeHtml(item.status)}">
      <span class="stack-dot" aria-hidden="true"></span>
      <div>
        <strong>${escapeHtml(item.source)} · ${escapeHtml(titleCase(item.status))}</strong>
        <small>${escapeHtml(item.claim)}</small>
      </div>
    </div>
  `).join("");
}

function controlMarkup(items) {
  return items.map((item) => `
    <div class="stack-item ${escapeHtml(item.status)}">
      <span class="stack-dot" aria-hidden="true"></span>
      <div>
        <strong>${escapeHtml(item.label)} · ${escapeHtml(titleCase(item.status))}</strong>
        <small>${escapeHtml(item.detail)}</small>
      </div>
    </div>
  `).join("");
}

function questionsMarkup(caseRecord) {
  const questions = caseRecord.open_questions.map((item) => ({
    label: "Open question",
    detail: `${item.question} Owner: ${item.owner}.`,
    status: item.blocks_action ? "block" : "review",
  }));
  const assumptions = (caseRecord.decision?.assumptions || []).map((item) => ({
    label: "Assumption",
    detail: item,
    status: "review",
  }));
  const items = [...questions, ...assumptions];
  if (!items.length) {
    return '<p class="empty-list">No unresolved question or unsupported assumption is hidden in this proposal.</p>';
  }
  return items.map((item) => `
    <div class="stack-item ${item.status}">
      <span class="stack-dot" aria-hidden="true"></span>
      <div><strong>${escapeHtml(item.label)}</strong><small>${escapeHtml(item.detail)}</small></div>
    </div>
  `).join("");
}

function auditMarkup(items) {
  return items.map((item) => `
    <div class="timeline-item">
      <span class="timeline-dot" aria-hidden="true"></span>
      <div>
        <strong>${escapeHtml(titleCase(item.event))}</strong>
        <small>${escapeHtml(item.actor)} · ${escapeHtml(item.detail)}</small>
      </div>
    </div>
  `).join("");
}

function renderImprovementOverview(overview) {
  state.improvement = overview;
  el("active-version").textContent = `v${overview.active_version}`;
  el("improvement-hypothesis").textContent = overview.hypothesis;
  el("improvement-boundary").textContent = overview.boundary;
  el("support-reuse-list").innerHTML = overview.reuse.map((item) => `
    <div class="reuse-item">
      <strong>${escapeHtml(item.name)}</strong>
      <small>${escapeHtml(item.role)}</small>
      <code>${escapeHtml(item.path)}</code>
    </div>
  `).join("");
  el("support-automation-list").innerHTML = overview.automations.map((item) => `
    <div class="reuse-item">
      <strong>${escapeHtml(item.name)}</strong>
      <small>${escapeHtml(item.purpose)}</small>
      <code>${escapeHtml(item.cadence)}</code>
    </div>
  `).join("");
  if (overview.last_run) {
    renderImprovementRun(overview.last_run);
  } else {
    el("improvement-empty").hidden = false;
    el("improvement-results").hidden = true;
  }
}

function versionEvidenceCard(version) {
  const spend = `$${Number(version.actual_model_spend_aud).toFixed(4)}`;
  return `
    <article class="version-card ${version.label.toLowerCase()}">
      <div class="version-card-heading">
        <span>${escapeHtml(version.label)}</span>
        <strong>v${escapeHtml(version.version)}</strong>
      </div>
      <div class="version-metrics">
        <div><strong>${escapeHtml(version.passed_cases)}/${escapeHtml(version.evaluation_cases)}</strong><small>support outcomes passed</small></div>
        <div><strong>${escapeHtml(version.model_calls_avoided)}</strong><small>provider calls avoided</small></div>
        <div><strong>${escapeHtml(version.prompt_token_proxy)}</strong><small>prompt token proxy</small></div>
        <div><strong>${escapeHtml(spend)}</strong><small>actual model spend AUD</small></div>
      </div>
      <p>${escapeHtml(version.prompt_path)} · ${escapeHtml(version.input_token_proxy + version.output_token_proxy)} total local token proxy across the run.</p>
    </article>
  `;
}

function renderImprovementRun(run) {
  el("improvement-empty").hidden = true;
  el("improvement-results").hidden = false;
  const recommendation = el("improvement-recommendation");
  recommendation.className = `recommendation-banner ${run.status}`;
  recommendation.innerHTML = `
    <span>Evidence recommendation</span>
    <strong>${escapeHtml(titleCase(run.recommendation))}</strong>
    <small>Status: ${escapeHtml(titleCase(run.status))}</small>
  `;
  el("version-comparison").innerHTML = versionEvidenceCard(run.active) + versionEvidenceCard(run.candidate);
  el("regression-count").textContent = `${run.candidate.passed_cases}/${run.candidate.evaluation_cases} passed`;
  el("regression-table").innerHTML = run.candidate.cases.map((item) => `
    <div class="regression-row ${item.passed ? "pass" : "fail"}">
      <span class="regression-result">${item.passed ? "Pass" : "Fail"}</span>
      <div><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(item.detail)}</small></div>
      <div><strong>${escapeHtml(titleCase(item.actual_state))}</strong><small>${escapeHtml(item.model_calls)} provider call${item.model_calls === 1 ? "" : "s"} · ${escapeHtml(item.required_control)}</small></div>
    </div>
  `).join("");
  el("improvement-evidence").innerHTML = run.evidence.map((item) => `
    <div class="stack-item pass"><span class="stack-dot" aria-hidden="true"></span><div><small>${escapeHtml(item)}</small></div></div>
  `).join("");
  el("improvement-controls").innerHTML = run.controls.map((item) => `
    <div class="stack-item review"><span class="stack-dot" aria-hidden="true"></span><div><small>${escapeHtml(item)}</small></div></div>
  `).join("");
  const canDecide = run.status === "awaiting_approval" && run.recommendation === "activate_candidate";
  el("approve-improvement").disabled = !canDecide;
  el("reject-improvement").disabled = run.status !== "awaiting_approval";
  el("change-owner").disabled = run.status !== "awaiting_approval";
  el("activation-copy").textContent = run.status === "approved"
    ? `v${run.candidate.version} is active after approval by ${run.decided_by}. The v1.0 prompt remains the rollback file.`
    : run.status === "rejected"
      ? `The candidate was rejected by ${run.decided_by}; v${run.active.version} remains active.`
      : "The regression runner can recommend a version, but only the named support workflow owner can activate it.";
}

async function refreshImprovement() {
  const overview = await fetchJson("/improvement/overview");
  renderImprovementOverview(overview);
}

async function runImprovement() {
  const button = el("run-improvement");
  button.disabled = true;
  button.textContent = "Running 12 controlled cases…";
  try {
    const run = await fetchJson("/improvement/evaluate", { method: "POST" });
    renderImprovementRun(run);
    await refreshImprovement();
    showToast(`Support regression complete: ${run.candidate.passed_cases}/${run.candidate.evaluation_cases} candidate outcomes passed.`);
  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Run support regression check";
  }
}

async function recordImprovementDecision(approved) {
  const owner = el("change-owner").value.trim();
  if (!owner) {
    showToast("A named support workflow owner is required.");
    return;
  }
  try {
    const run = await fetchJson("/improvement/decision", {
      method: "POST",
      body: JSON.stringify({
        approved,
        approved_by: owner,
        note: approved ? "Six-case legal-support regression and efficiency evidence reviewed." : "Keep active version; candidate not accepted.",
      }),
    });
    renderImprovementRun(run);
    await refreshImprovement();
    showToast(approved ? `v${run.candidate.version} activated by named approval.` : "Candidate rejected; active support prompt unchanged.");
  } catch (error) {
    showToast(error.message);
  }
}

function renderCase(caseRecord) {
  el("case-empty").hidden = true;
  el("case-view").hidden = false;
  const banner = el("status-banner");
  banner.className = `status-banner ${caseRecord.state}`;
  banner.textContent = statusCopy(caseRecord);
  el("case-subject").textContent = caseRecord.ticket.subject;
  el("case-body").textContent = `“${caseRecord.ticket.body}”`;
  el("confidence").textContent = caseRecord.decision
    ? `${Math.round(caseRecord.decision.confidence * 100)}% proposal confidence`
    : "No model call";
  el("proposal-content").innerHTML = proposalMarkup(caseRecord);
  el("evidence-count").textContent = `${caseRecord.evidence.length} item${caseRecord.evidence.length === 1 ? "" : "s"}`;
  el("control-count").textContent = `${caseRecord.controls.length} check${caseRecord.controls.length === 1 ? "" : "s"}`;
  el("evidence-list").innerHTML = evidenceMarkup(caseRecord.evidence);
  el("control-list").innerHTML = controlMarkup(caseRecord.controls);
  el("question-list").innerHTML = questionsMarkup(caseRecord);
  el("audit-list").innerHTML = auditMarkup(caseRecord.audit);

  const canDecide = caseRecord.state === "awaiting_approval";
  el("approve-case").disabled = !canDecide;
  el("reject-case").disabled = !canDecide;
  el("reviewer").disabled = !canDecide;
  el("review-note").disabled = !canDecide;
  el("decision-message").textContent = canDecide
    ? "Approval permits one bounded support action. Rejection produces no matter, access or communication side effect."
    : statusCopy(caseRecord);
  el("run-case").textContent = "Run again";
}

async function runSelectedCase() {
  if (!state.selectedId) return;
  const button = el("run-case");
  const original = button.textContent;
  button.disabled = true;
  button.textContent = "Checking evidence…";
  try {
    const caseRecord = await fetchJson(`/tickets/${encodeURIComponent(state.selectedId)}/investigate`, { method: "POST" });
    state.cases.set(state.selectedId, caseRecord);
    renderCase(caseRecord);
    renderScenarios();
    await refreshScorecard();
    await refreshImprovement();
    showToast(`Case result: ${titleCase(caseRecord.state)}.`);
  } catch (error) {
    showToast(error.message);
  } finally {
    button.disabled = false;
    button.textContent = state.cases.has(state.selectedId) ? "Run again" : original;
  }
}

async function recordDecision(approved) {
  if (!state.selectedId) return;
  const reviewer = el("reviewer").value.trim();
  if (!reviewer) {
    showToast("A named reviewer is required.");
    return;
  }
  const payload = {
    approved,
    approved_by: reviewer,
    note: el("review-note").value.trim() || null,
    review_minutes: 1.5,
    material_correction: false,
  };
  try {
    const caseRecord = await fetchJson(`/tickets/${encodeURIComponent(state.selectedId)}/approval`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.cases.set(state.selectedId, caseRecord);
    renderCase(caseRecord);
    renderScenarios();
    await refreshScorecard();
    showToast(approved ? "Named approval recorded; bounded support action executed." : "Proposal rejected; no action executed.");
  } catch (error) {
    showToast(error.message);
  }
}

function scoreValue(value, suffix = "") {
  return value === null || value === undefined ? "Not measured" : `${value}${suffix}`;
}

async function refreshScorecard() {
  const scorecard = await fetchJson("/demo/scorecard");
  const spend = scorecard.estimated_model_spend_aud === null
    ? "Rate not set"
    : `$${Number(scorecard.estimated_model_spend_aud).toFixed(4)}`;
  const cards = [
    { value: scorecard.runs, label: "Controlled runs", detail: "Every case, including safe stops." },
    { value: scoreValue(scorecard.accepted_without_material_correction_pct, "%"), label: "Accepted quality", detail: "Measured only after human review." },
    { value: scorecard.blocked_or_clarified, label: "Exceptions caught", detail: "Blocked or clarified before action." },
    { value: scorecard.model_calls, label: "Proposal-provider calls", detail: `${scorecard.input_tokens + scorecard.output_tokens} recorded tokens · cap ${scorecard.model_call_cap}.` },
    { value: spend, label: "Estimated model spend", detail: `Experiment cap: $${Number(scorecard.experiment_spend_cap_aud).toFixed(2)} AUD.` },
    { value: scorecard.unauthorised_actions, label: "Unauthorised actions", detail: "Immediate-stop safety measure." },
  ];
  el("scorecard-grid").innerHTML = cards.map((card) => `
    <article class="score-card">
      <strong>${escapeHtml(card.value)}</strong>
      <h3>${escapeHtml(card.label)}</h3>
      <p>${escapeHtml(card.detail)}</p>
    </article>
  `).join("");
  el("scorecard-note").textContent = scorecard.note;
  el("experiment-decision").textContent = titleCase(scorecard.decision);
}

async function resetDemo() {
  try {
    await fetchJson("/demo/seed", { method: "POST" });
    state.cases.clear();
    renderScenarios();
    if (state.selectedId) selectScenario(state.selectedId);
    await refreshScorecard();
    el("harvey-results").hidden = true;
    showToast("Synthetic cases and measurements reset.");
  } catch (error) {
    showToast(error.message);
  }
}

async function initialise() {
  try {
    const [brief, scenarios, improvement, harvey] = await Promise.all([
      fetchJson("/demo/brief"),
      fetchJson("/demo/scenarios"),
      fetchJson("/improvement/overview"),
      fetchJson("/harvey/overview"),
    ]);
    state.brief = brief;
    state.scenarios = document.body.dataset.workbenchView === "matter"
      ? scenarios.filter((scenario) => scenario.category === "matter_opening")
      : scenarios;
    renderBrief();
    renderScenarios();
    renderImprovementOverview(improvement);
    renderHarveyOverview(harvey);
    await refreshScorecard();
    selectScenario(state.scenarios[0]?.id || null);
  } catch (error) {
    showToast(`Demo could not load: ${error.message}`);
  }
}

el("run-case").addEventListener("click", runSelectedCase);
el("approve-case").addEventListener("click", () => recordDecision(true));
el("reject-case").addEventListener("click", () => recordDecision(false));
el("reset-demo").addEventListener("click", resetDemo);
el("run-improvement").addEventListener("click", runImprovement);
el("approve-improvement").addEventListener("click", () => recordImprovementDecision(true));
el("reject-improvement").addEventListener("click", () => recordImprovementDecision(false));
el("run-harvey").addEventListener("click", runHarveyEvaluation);
initialise();

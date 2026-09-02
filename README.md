# Legal Technology Support Control Room

**Optional presentation-only site:** [jacquesonline.github.io/ai-support-poc](https://jacquesonline.github.io/ai-support-poc/) — verify availability before relying on it.

**Related project:** [matter-opening-control-room](https://github.com/jacquesonline/matter-opening-control-room)

This standalone proof of concept shows how a Digital Systems Lead could connect an ABL-style matter transaction, an AI-enabled legal-technology support desk, Harvey-assisted legal work and governed continuous improvement.

ABL publicly announced an agreement with Harvey on 1 September 2025 after a trial and co-development period. That public fact provides context only. Every ticket, legal-work pack, prompt result, time comparison and outcome in this project is synthetic; none represents ABL's private Harvey configuration, matter data, adoption, cost or realised results.

This is not ABL data, architecture, configuration or a claim about its current support model. All people, matters, clients, systems and outcomes are fictional.

## 1. Non-technical overview

### What this repository is

The demonstration explores a practical question: how can legal professionals receive faster, more consistent technology support and make useful use of AI without handing important decisions to AI?

It begins with a familiar business event—opening a matter—then follows the support experience through access requests, everyday technology problems, Harvey-assisted legal work and ongoing review. The aim is a controlled service that prepares work, shows its evidence, stops when authority is missing and leaves accountable people in charge.

```text
request → check the evidence → prepare a recommendation → accountable person decides
       → perform one permitted action → record the result → review quality, risk and cost
```

### What the demonstration shows

- **Matter opening:** an approved request can be processed only after evidence, policy and named approval.
- **Safe replay:** an existing authoritative matter is reconciled instead of recreated.
- **Safe recovery:** a timeout after commit uses lookup-before-retry and avoids a duplicate matter.
- **Reference governance:** an unmapped office stops before provider use and routes to the mapping owner.
- **Information barriers:** support cannot infer or grant restricted-matter access; the barrier owner retains authority.
- **General IT:** a document-management issue uses safe knowledge guidance without requesting document content or credentials.
- **Reuse:** project-local skills and prompts preserve the evidence, proposal, control, approval and measurement pattern.
- **Continuous improvement:** active and candidate prompts run through the same six cases before a named owner can activate a version.
- **Cost oversight:** model calls, local token proxy, actual or estimated spend, hard call caps, review caps and non-AI alternatives are visible beside quality.
- **Harvey enablement:** litigation preparation, research and first drafting, due diligence and knowledge reuse are bounded hypotheses with sources, permissions and lawyer verification.
- **Harvey pilot readiness:** each legal-work idea must have a defined need, source contract, output contract, lawyer review gate, measures, ownership and stop conditions before a bounded pilot. The POC does not claim the business benefit is already proven.

### What it does not claim

- It does not describe ABL's current systems, support model, data, permissions or Harvey configuration.
- It does not use real people, clients, matters, documents or legal work.
- It does not show that AI has already improved quality, saved money, increased profit or changed a court outcome.
- It does not allow AI to approve itself, grant access, change controlled reference data or make a legal decision.

### Who benefits if the approach is proven

- **Partners:** more reviewable starting work and more capacity for judgement, strategy and client leadership.
- **Lawyers:** less repetitive preparation, with sources, limitations and verification requirements made visible.
- **Staff:** safer self-service and a clear path to a responsible support owner.
- **Technology leaders:** evidence about service quality, adoption, risk, relevance and full operating cost before deciding to scale.

### Presentation boundary

The remotely shareable material is the working synthetic application, its evidence and tests, and the audience-safe architecture and control documentation. Presenter scripts, timings, likely-question answers, rehearsal notes and recovery instructions are maintained locally under `documents/demo/` and are deliberately excluded from version control and panel sharing.

For a local presentation, open the [executive overview](http://127.0.0.1:8017/), the [proof-point chooser](http://127.0.0.1:8017/workbench) and [The Demo's Rationale](http://127.0.0.1:8017/cheatsheet). These pages are audience-safe; the local presenter documents are not part of the shared pack.

## 2. Technical community guide

### Architecture and design

The application combines deterministic controls with a proposal provider that has no execution authority. Stable identifiers, reference validation, restricted-matter checks, approval gates and call/cost caps are enforced outside the model. The design is anchored in the related Matter Opening Control Room pattern: lookup before create, safe replay, timeout recovery and authoritative reconciliation.

Detailed references:

- [Architecture and control boundaries](documents/general/ARCHITECTURE.md)
- [Visual and brand system](documents/general/BRAND_SYSTEM.md)
- [Private-sharing guidance](documents/general/PRIVATE_SHARING.md)

### Repository structure

- `app/` — FastAPI application, synthetic workflows, policy controls and presentation UI.
- `tests/` — credential-free integration and control tests.
- `documents/demo/` — local-only presenter preparation; ignored by version control and excluded from remote sharing.
- `documents/general/` — architecture, sharing and visual-design documentation.
- `prompts/` — active, candidate, oversight and Harvey legal-work prompts.
- `skills/` — reusable support, improvement, Harvey-work and value-review packages.
- `governance/` — activation, rollback, stop and ownership contracts.
- `automations/` — review definitions; these are examples, not live scheduled jobs.
- `scripts/` and `share/` — static presentation export and supporting assets.

### Run locally

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\start-demo.ps1
```

The default mode is credential-free and uses only in-memory synthetic data. Matter and Support are two proofs within one governed operating model, not two applications. [Matter opening](http://127.0.0.1:8017/workbench/matter) is the depth proof: four transaction conditions test authoritative reconciliation, duplicate prevention, reference control and safe recovery. [Support](http://127.0.0.1:8017/workbench/support) is the transferability proof: two non-transaction requests test whether the same evidence, control and human-authority pattern travels to restricted access and general IT. The [continuous-improvement](http://127.0.0.1:8017/workbench/improvement) regression recombines all six to test the shared method. Separate focused pages remain available for [Harvey](http://127.0.0.1:8017/workbench/harvey) and [value](http://127.0.0.1:8017/workbench/value).

The presentation-only GitHub Pages edition can be published at [jacquesonline.github.io/ai-support-poc](https://jacquesonline.github.io/ai-support-poc/) after the repository visibility and Pages configuration have been deliberately approved and verified. GitHub Pages cannot run the FastAPI backend, so interactive ticket actions and evaluation runs remain available only in the local application. The local application is the authoritative demonstration; the Pages workflow exports the overview, proof pages, selector and rationale after each push to `main` when hosting is enabled.

### Local demonstration route

The ignored local file `documents/demo/DEMO_GUIDE.md` is the presenter source of truth for sequence, timing and likely questions. Those interview-preparation details are intentionally absent from the remote repository.

### Six-case regression contract

| Case | Expected result | Proof |
|---|---|---|
| Approved matter not available | Awaiting approval | Proposal cannot create a matter itself |
| Replay could create a duplicate | Awaiting approval | Existing authoritative matter produces an idempotent no-op |
| Unmapped office reference | Blocked before provider | Support cannot alter controlled reference data |
| Timeout after matter creation | Awaiting approval | Lookup-before-retry recovers an ambiguous commit |
| Restricted matter access | Blocked before provider | Information-barrier owner retains access authority |
| Document add-in unavailable | Awaiting approval | Guidance minimises data and excludes content and credentials |

### Reusable and reviewable assets

#### `skills/`

Contains four reusable workflow packages. Each package separates the operating instructions, agent-facing metadata and detailed control contract so the method can be inspected and versioned.

- `legal-support-resolution/SKILL.md` — governs evidence-bound triage for matter opening, replay, recovery, restricted access and general IT requests.
- `legal-support-resolution/references/control-contract.md` — defines permitted evidence, mandatory stops, required outputs and actions the support workflow may not take.
- `legal-support-resolution/agents/openai.yaml` — provides the agent metadata used to present and invoke the legal-support resolution skill.
- `legal-support-improvement/SKILL.md` — evaluates active and candidate support workflows against the same six synthetic cases before a version decision.
- `legal-support-improvement/references/review-contract.md` — specifies the regression evidence and the activate, keep, reject or stop decisions available to the owner.
- `legal-support-improvement/agents/openai.yaml` — provides the agent metadata for the support-improvement skill.
- `harvey-legal-work/SKILL.md` — frames source-grounded, lawyer-reviewed litigation, research, due-diligence and knowledge-reuse work.
- `harvey-legal-work/references/work-product-contract.md` — defines the required brief, reviewable output sections and prohibited autonomous legal outcomes.
- `harvey-legal-work/agents/openai.yaml` — provides the agent metadata for the governed Harvey legal-work skill.
- `harvey-value-review/SKILL.md` — reviews Harvey use cases for quality, adoption, continuing relevance, governance and total cost.
- `harvey-value-review/references/value-contract.md` — defines the quality, economics, governance and stop evidence required for a value decision.
- `harvey-value-review/agents/openai.yaml` — provides the agent metadata for the Harvey value-review skill.

#### `prompts/`

Contains the versioned task instructions used by the support regression and the four synthetic Harvey legal-work patterns.

- `support-investigation.md` — active v1.0 instructions for investigating a legal-technology support request.
- `support-investigation.v1.1-candidate.md` — inactive candidate that removes instructions already enforced by deterministic controls.
- `support-regression-review.md` — compares prompt versions against the six-case support contract and reports regressions without activating a change.
- `support-oversight.md` — supports quality, relevance, governance, cost and safer-alternative review decisions.
- `harvey-litigation-preparation.md` — structures chronology, issue, evidence-gap and source-backed litigation preparation.
- `harvey-legal-research.md` — structures jurisdiction-aware legal research and a lawyer-reviewable first draft.
- `harvey-diligence-review.md` — structures consistent document review against an approved issue taxonomy.
- `harvey-knowledge-reuse.md` — supports permission-aware selection and adaptation of current precedents and playbooks.

#### `governance/`

Contains the decision rights, evidence requirements and change controls that sit around the prompts and skills.

- `change-policy.md` — defines ownership, required evidence, approval, rollback and stop rules for governed changes.
- `change-log.md` — records the purpose and control changes introduced by each proof-of-concept version.
- `support-improvement-contract.md` — defines the improvement hypothesis, generated evidence, activation boundary and rollback position for support prompts.
- `harvey-operating-contract.md` — defines Harvey decision rights, legal outcome boundaries and the evidence required before scaling a use case.

#### `automations/`

Contains review schedules and triggers represented as inspectable definitions rather than live production jobs.

- `support-review-register.json` — defines change-triggered regression, weekly outcome and monthly relevance/cost reviews for support and Harvey workflows, including owners and stop conditions.

The automation register does not schedule a live ABL job or send notifications.

### What better outcomes mean

- **In court:** stronger preparation evidence—issue coverage, chronology completeness, contrary-authority checks and citation integrity—not a prediction or attribution of a court result.
- **For partners:** more reviewable starting work and capacity for strategy, supervision and client leadership.
- **For lawyers:** less repetitive extraction and drafting, with sources, limitations and verification visible.
- **For staff:** safer self-service, current knowledge and a support path when an AI workflow should stop.
- **For profit and cost:** accepted capacity, write-downs, fixed-fee margin, realised revenue and full run cost; model-produced minutes are not directly converted into profit.

### Tests

```powershell
python -m pytest -q
```

The credential-free suite covers all six service-desk cases, matter idempotency and recovery, reference and information-barrier stops, data minimisation, call and cost caps, active/candidate regression, named activation and rejection without a version change.

### Optional live adapters and production boundary

The OpenAI and Zammad adapters remain optional technical extension points. Use them only with approved accounts, synthetic data, current approved rates and organisation-specific security controls. Pricing is not hard-coded; when rates are absent, a live-model action is blocked rather than assigned an invented cost.

Production use would still require verified systems of record, authentication and RBAC, privilege and privacy design, durable audit and decision records, supported vendor interfaces, webhook validation, queues and bounded retry, monitoring, incident response, records management, evaluation data approval and operating ownership.

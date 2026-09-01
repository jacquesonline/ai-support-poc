# Legal Technology Support Control Room

A standalone demonstration of how a Digital Systems Lead could connect an ABL-style matter transaction, an AI-enabled legal-technology support desk, Harvey-assisted legal work and governed continuous improvement.

ABL publicly announced an agreement with Harvey on 1 September 2025 after a trial and co-development period. That public fact provides context only. Every ticket, legal-work pack, prompt result, time comparison and outcome in this project is synthetic; none represents ABL's private Harvey configuration, matter data, adoption, cost or realised results.

It is anchored in the Matter Opening Control Room pattern: stable intake identifiers, approved requests, reference-data validation, lookup-before-create, safe replay, timeout recovery, authoritative matter identifiers and business reconciliation. It adds everyday service-desk triage, restricted-matter access and document-management support.

This is not ABL data, architecture, configuration or a claim about its current support model. All people, matters, clients, systems and outcomes are fictional.

```text
legal-professional ticket
        ↓
minimum permitted evidence
        ↓
deterministic matter / access / data controls ──stop or route──► named specialist owner
        ↓ pass
structured AI proposal with no execution authority
        ↓
named support approval
        ↓
bounded synthetic action + professional reply
        ↓
quality, speed, governance, usage and cost evidence
        ↓
six-case regression + relevance review + governed prompt version
```

## What the demo proves

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

## Run locally

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
.\start-demo.ps1
```

Open the [executive overview](http://127.0.0.1:8017/). The default mode is credential-free and uses only in-memory synthetic data. The [proof-point chooser](http://127.0.0.1:8017/workbench), [Demo's Rational](http://127.0.0.1:8017/cheatsheet) and optional [full evidence workbench](http://127.0.0.1:8017/workbench/full) are separate routes.

The presentation-only GitHub Pages edition is published at [jacquesonline.github.io/ai-support-poc](https://jacquesonline.github.io/ai-support-poc/). GitHub Pages cannot run the FastAPI backend, so interactive ticket actions and evaluation runs remain available in the local application. The Pages workflow exports the overview, proof pages, selector and rationale after each push to `main`.

## CIO demonstration route

1. State the ABL-style hypothesis and explicit non-current-state boundary.
2. Run **Approved matter not yet available** and approve it as the named support owner.
3. Run **Replay could create a duplicate** or **Timeout after matter creation** to show stable-ID and safe-recovery controls.
4. Run **Unmapped office reference** and **Restricted matter access**; both stop before provider use and reject an approval override.
5. Run **Document add-in unavailable** to show safe day-to-day IT guidance and data minimisation.
6. Run the four-use-case Harvey readiness review. Show that every proposed pilot has sources, review, measures and stops, while quality, time and value remain unproven until representative ABL work is evaluated.
7. Make the evidence boundary explicit: the readiness review proves the pilot design, while quality, capacity and financial value require representative ABL work, a baseline and full operating cost.
8. Run the six-case prompt regression and show that activation remains a named decision.
9. Close on change-triggered regression, weekly adoption and quality review, monthly relevance and total-cost decisions, and the option to change, replace, retire or stop.

See `DEMO_GUIDE.md` for the spoken route.

## Six-case regression contract

| Case | Expected result | Proof |
|---|---|---|
| Approved matter not available | Awaiting approval | Proposal cannot create a matter itself |
| Replay could create a duplicate | Awaiting approval | Existing authoritative matter produces an idempotent no-op |
| Unmapped office reference | Blocked before provider | Support cannot alter controlled reference data |
| Timeout after matter creation | Awaiting approval | Lookup-before-retry recovers an ambiguous commit |
| Restricted matter access | Blocked before provider | Information-barrier owner retains access authority |
| Document add-in unavailable | Awaiting approval | Guidance minimises data and excludes content and credentials |

## Reusable and reviewable assets

- `skills/legal-support-resolution/` — governed matter, access and general-IT triage.
- `skills/legal-support-improvement/` — six-case version and regression review.
- `skills/harvey-legal-work/` — source-grounded Harvey work-product contract.
- `skills/harvey-value-review/` — adoption, quality, relevance and commercial evidence review.
- `prompts/harvey-*.md` — four synthetic legal-work patterns.
- `prompts/support-investigation.md` — active v1.0 prompt.
- `prompts/support-investigation.v1.1-candidate.md` — inactive candidate.
- `prompts/support-regression-review.md` — support-specific regression contract.
- `prompts/support-oversight.md` — quality, relevance, governance and cost decision prompt.
- `automations/support-review-register.json` — change-triggered, weekly and monthly review definitions.
- `governance/` — activation, rollback, stop and ownership controls.

The automation files demonstrate schedules and review contracts; they do not create a live ABL job or send notifications.

## What better outcomes mean

- **In court:** stronger preparation evidence—issue coverage, chronology completeness, contrary-authority checks and citation integrity—not a prediction or attribution of a court result.
- **For partners:** more reviewable starting work and capacity for strategy, supervision and client leadership.
- **For lawyers:** less repetitive extraction and drafting, with sources, limitations and verification visible.
- **For staff:** safer self-service, current knowledge and a support path when an AI workflow should stop.
- **For profit and cost:** accepted capacity, write-downs, fixed-fee margin, realised revenue and full run cost; model-produced minutes are not directly converted into profit.

## Tests

```powershell
python -m pytest -q
```

The credential-free suite covers all six service-desk cases, matter idempotency and recovery, reference and information-barrier stops, data minimisation, call and cost caps, active/candidate regression, named activation and rejection without a version change.

## Optional live adapters

The OpenAI and Zammad adapters remain optional technical extension points. Use them only with approved accounts, synthetic data, current approved rates and organisation-specific security controls. Pricing is not hard-coded; when rates are absent, a live-model action is blocked rather than assigned an invented cost.

Production use would still require verified systems of record, authentication and RBAC, privilege and privacy design, durable audit and decision records, supported vendor interfaces, webhook validation, queues and bounded retry, monitoring, incident response, records management, evaluation data approval and operating ownership.

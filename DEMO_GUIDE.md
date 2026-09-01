# CIO legal-support and Harvey demonstration guide

## Opening — why this approach

> This starts with a system ABL people recognise: matter opening. The support POC then shows how I would help lawyers, partners and staff get reliable outcomes across matters, access and general IT. Harvey extends the same discipline into legal work. Prompts make the task explicit, skills preserve repeatable practice, automations keep it tested and relevant, and governance keeps authority, sources, access and spend visible.

Use the four-part journey on screen: legal transaction → support operating layer → Harvey enablement → continuous improvement. State that ABL's Harvey agreement is public, while all demonstrated use cases and results are synthetic.

When showing the Harvey readiness assessment, say:

> This does not prove Harvey improves quality or saves money. It proves that I have converted four legal-work ideas into controlled pilot designs, each with a need, source boundary, output contract, lawyer review, measures and stops. Representative ABL work and a baseline would be required to establish the benefit.

## Start — choose the proof point

Open `http://127.0.0.1:8017/workbench`. Use the five-button selector to choose one focused proof. Do not begin in the full evidence workbench.

Use `http://127.0.0.1:8017/cheatsheet` for the first-person rationale and evidence table.

## 0:00–0:45 — frame the approach

> I have not assumed ABL's current support process or configuration. This synthetic demonstration asks how an AI-assisted legal-technology support desk could improve triage and reuse while matter, access and communication decisions remain controlled and human-owned.

Point to the boundary, candidate outcomes and principle: **AI prepares. Policy constrains. People decide.**

## 0:45–2:10 — normal matter opening

Run **Approved matter not yet available**.

Show the synthetic ticket, approved intake, office and practice references, absence of an authoritative target matter, structured proposal and named approval. Approve it.

> The useful outcome is not a polished answer. It is one reconciled matter action, with its intake ID, approver, target ID and audit evidence preserved.

## 2:10–3:10 — idempotency and recovery

Run **Replay could create a duplicate** or **Timeout after matter creation**.

Explain that an existing matter produces a no-op and an ambiguous timeout requires lookup-before-retry. A blind create retry is never delegated to AI.

## 3:10–4:15 — privilege and ownership boundaries

Run **Unmapped office reference** and **Restricted matter access**.

Both stop before provider use. Point to the named reference-data or information-barrier owner and disabled approval path.

> Governance is workflow behaviour: support cannot use a persuasive proposal to override controlled master data or a restricted-matter decision.

## 4:15–5:00 — everyday legal-professional IT

Run **Document add-in unavailable**.

Show the approved knowledge evidence and data-minimisation control. The guidance requests only a visible error code and explicitly excludes document content and credentials.

## 5:00–7:10 — continuous improvement of this desk

Run **Legal support regression check**.

Show:

- the same six cases for v1.0 and v1.1;
- exact state and control results;
- four provider calls and two deterministic pre-provider stops per version;
- prompt characters and transparent local token proxy from the actual files;
- zero paid model spend in credential-free mode;
- the hard eight-call review cap; and
- the inactive recommendation.

Approve v1.1 as the named legal-technology support owner.

> A prompt, skill or automation is a governed support asset. It has a purpose, owner, version, evaluation set, review trigger, cost boundary and rollback path. The review can recommend a change but cannot approve itself.

## 7:10–8:00 — relevance, cost and questions

Point to the experiment scorecard and ongoing review definitions.

> In a real bounded trial I would add representative de-identified tickets, reviewer corrections, time to owned action, adoption, incidents and full operating cost. The monthly decision is not automatically “more AI”; it may be keep, narrow, replace with a rule or knowledge article, roll back, retire or stop.

Ask:

> Where does ABL's current legal-technology support lifecycle lose the most time or quality, which decision boundaries are non-negotiable, and what evidence would make this experiment worth continuing?

## Demonstration safety

- Use `AI_PROVIDER=fake` and `TICKET_BACKEND=memory`.
- Confirm the header says `Synthetic · not ABL configuration`.
- Reset, run the six cases and regression once, then reset again.
- Do not open unrelated private workspaces during the demonstration.
- Keep unrelated applications, notifications and recent items closed.
- Describe all product boundaries as hypotheses until ABL confirms its actual platforms and ownership model.

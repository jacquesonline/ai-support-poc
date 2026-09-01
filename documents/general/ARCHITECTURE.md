# Legal support architecture and control boundaries

## System view

```text
Synthetic legal-professional ticket
          │
          ▼
Category + minimum permitted evidence
          │
          ├─ Matter Opening Control Room: intake, approval, mapping, target lookup, execution state
          ├─ Information-barrier register: restricted status and access owner only
          └─ Approved knowledge article: safe steps and prohibited data
          │
          ▼
Deterministic pre-checks ──block/clarify──► named matter, mapping or access owner
          │ pass
          ▼
Structured proposal provider — no matter, access or communication tools
          │
          ▼
Deterministic policy + cost cap
          │
          ▼
Named support decision ──reject──► no side effect
          │ approve
          ▼
One permitted synthetic action + reply
          │
          ▼
Audit, outcome, usage, cost and six-case regression evidence
```

## Matter Opening Control Room relationship

The Python POC reuses the synthetic Matter Opening Control Room contract as its operational base:

- `INT-2401` — approved request and controlled normal creation;
- `INT-2402` — authoritative matter already exists, so replay becomes an idempotent no-op;
- `INT-2403` — unmapped office becomes an owned exception before provider use; and
- `INT-2404` — timeout after commit is recovered by lookup-before-retry.

The design remains product-neutral. Intake and financial-system names represent conceptual boundaries only; real ABL modules, APIs, ownership and data contracts must be confirmed.

## Decision rights

| Participant | May do | May not do |
|---|---|---|
| Proposal provider | Summarise supplied evidence and propose one next action | Create a matter, change mappings, grant access, approve itself or contact a user |
| Matter control layer | Validate approval/reference data, lookup by stable ID and process one approved action | Guess a reference value or blind-retry an ambiguous create |
| Information-barrier check | Identify restricted status and named owner | Reveal matter content or decide access |
| Named support owner | Approve or reject eligible matter/general-IT actions | Override mapping or information-barrier blockers through this endpoint |
| Mapping/access owner | Decide the specialist exception under real policy | Delegate authority to the proposal provider |
| Digital systems lead | Decide keep, change, non-AI alternative, rollback or stop | Claim production value from synthetic results |

## Improvement path

```text
active v1.0 ─┐
             ├─► same six legal-support cases ─► outcome / authority / usage evidence
candidate ───┘                                  │
                                                ▼
                           recommend only; candidate remains inactive
                                                │
                                                ▼
                                named legal-support owner decision
                                  │ approve              │ reject
                                  ▼                      ▼
                              activate v1.1          keep v1.0
```

The runner calculates a local token proxy from actual prompt and payload characters and records zero actual model spend in credential-free mode. Provider-reported tokens and a cost estimate are used only with an approved live adapter and supplied rates. Quality, review, rework, incidents and non-AI alternatives remain part of total-cost oversight.

## Production omissions

This is not an authentication or authorisation system. Production would require verified sources, least privilege, ethical-wall and privilege review, durable queues and event records, concurrent idempotency, vendor-supported APIs, secrets, monitoring, incident response, privacy and records controls, approved evaluation data, service ownership and disaster recovery.

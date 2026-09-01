---
id: prompt.legal-support-regression-review
version: 1.0.0
status: active
owner: Legal technology support owner
purpose: Compare active and candidate prompts against the legal-support outcome contract.
---

# Legal support regression review

Run both prompt versions through the same six synthetic cases: normal matter opening, duplicate replay, unmapped office, timeout recovery, restricted access and document-management IT support.

Verify exact states, deterministic controls, pre-provider stops, blocked approval overrides, provider calls avoided, prompt size, local token proxy, actual spend and unauthorised actions. Return `activate_candidate`, `keep_active`, `reject_candidate` or `stop`. The review cannot activate its recommendation.

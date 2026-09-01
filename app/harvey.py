"""Synthetic Harvey enablement and value evidence for the CIO demonstration."""

from datetime import datetime, timezone


PUBLIC_CONTEXT = {
    "statement": (
        "ABL publicly announced an agreement with Harvey on 1 September 2025 following a successful "
        "trial and co-development period focused on legal, business and client needs."
    ),
    "boundary": (
        "The use cases below are synthetic operating hypotheses. They do not represent ABL's private "
        "Harvey configuration, matter content, permissions, adoption, cost or realised outcomes."
    ),
    "sources": [
        {
            "label": "ABL AI investment announcement",
            "url": "https://www.abl.com.au/insights-and-news/abl-announces-new-investment-in-ai-driven-technology/",
            "supports": "Agreement, trial/co-development and stated document-analysis, routine-task and insight objectives.",
        },
        {
            "label": "Harvey platform overview",
            "url": "https://help.harvey.ai/articles/getting-started-with-harvey",
            "supports": "Assistant, Vault, Workflow Agents, History and Library capabilities.",
        },
        {
            "label": "Harvey Vault",
            "url": "https://www.harvey.ai/platform/vault",
            "supports": "Document review, review tables, knowledge bases and permission controls.",
        },
    ],
}


USE_CASES = [
    {
        "id": "litigation-preparation",
        "name": "Litigation preparation",
        "primary_users": "Partners, senior lawyers and litigation teams",
        "harvey_surfaces": "Vault, Review Tables and Assistant",
        "need": "Build a reliable chronology, issue matrix and source-backed argument framework from a large matter set.",
        "better_outcome": "More complete preparation, earlier gap detection and stronger source discipline for lawyer-led advocacy.",
        "not_claimed": "Harvey does not determine strategy, advocacy or the court result.",
        "prompt_path": "prompts/harvey-litigation-preparation.md",
        "skill_path": "skills/harvey-legal-work/SKILL.md",
    },
    {
        "id": "legal-research-draft",
        "name": "Research and first draft",
        "primary_users": "Lawyers and partners",
        "harvey_surfaces": "Assistant, legal knowledge sources and Word",
        "need": "Create a source table and reviewable first-draft structure without losing jurisdiction, currency or contrary authority.",
        "better_outcome": "Faster route to a lawyer-verified draft with visible authorities, gaps and counterarguments.",
        "not_claimed": "The output is not final advice and every material proposition requires lawyer verification.",
        "prompt_path": "prompts/harvey-legal-research.md",
        "skill_path": "skills/harvey-legal-work/SKILL.md",
    },
    {
        "id": "diligence-review",
        "name": "Due-diligence review",
        "primary_users": "Transactional teams and partners",
        "harvey_surfaces": "Vault, Review Tables and Workflow Agents",
        "need": "Review a document set consistently against an approved issue taxonomy and expose red flags for lawyer judgement.",
        "better_outcome": "More consistent issue coverage, structured review evidence and capacity for higher-value analysis.",
        "not_claimed": "Extraction is not the final legal or commercial risk decision.",
        "prompt_path": "prompts/harvey-diligence-review.md",
        "skill_path": "skills/harvey-legal-work/SKILL.md",
    },
    {
        "id": "knowledge-reuse",
        "name": "Precedent and knowledge reuse",
        "primary_users": "Lawyers, graduates, knowledge teams and support staff",
        "harvey_surfaces": "Vault knowledge bases, Library and Assistant",
        "need": "Find current, permission-appropriate precedents and playbooks without rediscovery or cross-matter leakage.",
        "better_outcome": "Faster, more consistent starting work with limitations and superseded material visible.",
        "not_claimed": "A precedent is not automatically current or suitable for the matter.",
        "prompt_path": "prompts/harvey-knowledge-reuse.md",
        "skill_path": "skills/harvey-legal-work/SKILL.md",
    },
]


class HarveyValueService:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.runs: list[dict] = []

    def overview(self) -> dict:
        return {
            "public_context": PUBLIC_CONTEXT,
            "journey": [
                {"step": "01", "name": "Legal transaction", "detail": "Matter Opening Control Room makes the daily system and control context concrete."},
                {"step": "02", "name": "Support operating layer", "detail": "The helpdesk improves matter, access and general-IT outcomes without taking authority."},
                {"step": "03", "name": "Harvey enablement", "detail": "Lawyers use approved AI patterns for analysis, drafting, review and knowledge reuse."},
                {"step": "04", "name": "Continuous improvement", "detail": "Prompts, skills and workflows are measured, reviewed, versioned and retired when no longer valuable."},
            ],
            "users": [
                {"role": "Partners", "outcome": "Faster insight and more space for judgement, strategy and client leadership."},
                {"role": "Lawyers", "outcome": "Source-grounded starting work, fewer avoidable omissions and less repetitive preparation."},
                {"role": "Staff", "outcome": "Approved self-service workflows, knowledge access and responsive support."},
                {"role": "CIO / Digital Systems Lead", "outcome": "Visible adoption, quality, risk, relevance, support demand and total cost."},
            ],
            "use_cases": [{key: value for key, value in item.items() if key != "synthetic"} for item in USE_CASES],
            "decision_model": [
                "Use Harvey for variable legal analysis, extraction, drafting and reusable workflows over approved sources.",
                "Use deterministic systems for matter identity, permissions, information barriers, retention, approval and cost caps.",
                "Use lawyers for legal judgement, verification, advice, filings, advocacy and client decisions.",
                "Use non-AI search, precedent, rules or conventional automation when they are safer or cheaper.",
            ],
            "last_run": self.runs[-1] if self.runs else None,
        }

    def evaluate(self) -> dict:
        results = [
            {
                "id": item["id"],
                "name": item["name"],
                "ready_for_controlled_pilot": True,
                "readiness_checks": {
                    "business_need_defined": bool(item["need"]),
                    "approved_source_scope_required": True,
                    "structured_output_contract": bool(item["prompt_path"]),
                    "reusable_skill_defined": bool(item["skill_path"]),
                    "lawyer_review_required": True,
                    "autonomous_legal_action": False,
                    "quality_and_cost_measures_required": True,
                },
                "pilot_must_measure": [
                    "Lawyer acceptance and material corrections",
                    "Source and citation verification",
                    "Issue omissions and review effort",
                    "Elapsed and active handling time against baseline",
                    "Licence, support, training and review cost",
                    "Privacy, privilege, access and reliability incidents",
                ],
                "detail": item["better_outcome"],
            }
            for item in USE_CASES
        ]
        run = {
            "id": f"harvey-readiness-{len(self.runs) + 1:02d}",
            "status": "pilot_design_ready",
            "recommendation": "run_bounded_pilot_with_approved_abl_data_and_owners",
            "synthetic": True,
            "results": results,
            "readiness": {
                "use_cases_ready_for_controlled_pilot": len(results),
                "total_use_cases": len(results),
                "source_contracts_required": len(results),
                "lawyer_review_gates": len(results),
                "autonomous_legal_actions": 0,
                "real_outcome_evidence_available": False,
            },
            "economics": {
                "harvey_licence_cost_aud": None,
                "integration_support_training_cost_aud": None,
                "cost_per_accepted_work_product_aud": None,
                "realised_profit_impact_aud": None,
                "status": "Cannot conclude economics until approved ABL cost and reviewed outcome data are supplied.",
            },
            "evidence_boundary": (
                "This assessment proves that each use case has a defined need, source boundary, output contract, "
                "lawyer review gate, measurement plan and stop conditions. It does not prove that Harvey improves "
                "quality, saves time, increases profit or changes a legal outcome. Those claims require a bounded "
                "pilot using approved representative work and reviewed baseline evidence."
            ),
            "court_outcome_boundary": (
                "The proposed pilot would measure preparation completeness, source integrity and reviewability. "
                "It would not predict or attribute a court result to Harvey."
            ),
            "governance": [
                "Approved matter and knowledge scope before use",
                "Information-barrier and permission enforcement outside prompts",
                "Lawyer verification for every material proposition",
                "No filing, advice, court or client communication by the workflow",
                "Prompt/workflow owner, version, evaluation set and rollback",
                "Monthly relevance, adoption and total-cost decision",
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.runs.append(run)
        return run

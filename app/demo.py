"""Synthetic ABL-style legal-technology support-desk scenarios."""

from app.models import Ticket
from app.tickets import MemoryTicketAdapter


DEMO_BRIEF = {
    "title": "Legal Technology Support Control Room",
    "stage": "Bounded experiment",
    "boundary": (
        "Synthetic ABL-style service-desk hypothesis. Not ABL data, configuration or a claim about its current systems."
    ),
    "hypothesis": (
        "If a legal-technology support desk uses AI to prepare evidence-bound triage and resolution proposals, "
        "while matter, access, policy and approval controls remain deterministic and human-owned, it can improve "
        "quality, reuse and speed without exposing privileged information or creating uncontrolled cost."
    ),
    "business_questions": [
        "Which matter-lifecycle and general IT requests create the most avoidable handling or rework?",
        "Which matter, client, identity and access sources are authoritative for each request type?",
        "Which decisions must remain with risk, information-barrier, records or service owners?",
        "What would legal professionals and support reviewers accept without material correction?",
        "What is the total cost per accepted resolution, including review, rework and exceptions?",
        "What privacy, privilege, access or reliability event would make us stop?",
    ],
    "users": [
        {"role": "Legal professional", "need": "Timely help without repeating context or exposing matter content."},
        {"role": "Service-desk analyst", "need": "Authoritative evidence and a consistent next-step proposal."},
        {"role": "Matter or access owner", "need": "Visible exceptions and retained decision authority."},
        {"role": "Digital systems lead", "need": "Quality, adoption, risk, cost and relevance evidence."},
    ],
    "outcomes": [
        {"name": "Ready to work", "measure": "Time from approved instruction to a usable matter—or a clearly owned exception with a next action.", "target": "Agree the service baseline and SLA"},
        {"name": "Right first time", "measure": "Openings completed without a correction, reopened ticket or repair to controlled matter data.", "target": "Improve against the measured baseline"},
        {"name": "Less chasing", "measure": "Support touches, hand-offs and follow-up messages before the lawyer can continue working.", "target": "Reduce avoidable contacts and hand-offs"},
        {"name": "No harmful shortcut", "measure": "Duplicate matters, blind retries, unauthorised access or changes to controlled reference data.", "target": "0"},
    ],
    "stop_criteria": [
        "Suspected exposure of privileged, restricted, personal or unnecessary matter information.",
        "An unauthorised matter creation, access grant, reference-data change or user communication.",
        "A duplicate matter is created or an ambiguous commit is blindly retried.",
        "An accepted proposal contains an unsupported consequential statement.",
        "Review and rework remove the handling-time benefit, or total cost exceeds value.",
        "A rule, knowledge article, search or conventional automation is more reliable or economical.",
    ],
}


SCENARIOS = [
    {
        "id": "1",
        "name": "Approved matter not yet available",
        "description": "A partner asks support to check approved intake INT-2401; creation remains approval-controlled.",
        "expected": "awaiting_approval",
        "required_control": "human-approval",
        "approval_test": "execute",
        "ticket": Ticket(
            id="1",
            subject="Approved matter INT-2401 is not available",
            body="INT-2401 was approved, but the new matter is not yet available for time recording. Please investigate.",
            requester="partner.104@example.test",
            requester_role="Partner",
            category="matter_opening",
        ),
    },
    {
        "id": "2",
        "name": "Replay could create a duplicate",
        "description": "INT-2402 already has an authoritative matter; the workflow must reconcile instead of recreate.",
        "expected": "awaiting_approval",
        "required_control": "stable-intake-id",
        "approval_test": "none",
        "ticket": Ticket(
            id="2",
            subject="Retry requested for INT-2402",
            body="The opening job for INT-2402 was resubmitted. Please make sure the matter is available without creating a duplicate.",
            requester="lawyer.218@example.test",
            requester_role="Senior associate",
            category="matter_opening",
        ),
    },
    {
        "id": "3",
        "name": "Unmapped office reference",
        "description": "INT-2403 contains MEL-X; support must route the owned exception rather than change master data.",
        "expected": "blocked",
        "required_control": "office-reference",
        "approval_test": "block",
        "ticket": Ticket(
            id="3",
            subject="Matter opening exception for INT-2403",
            body="INT-2403 failed during matter opening. Can support correct it and rerun the request?",
            requester="partner.104@example.test",
            requester_role="Partner",
            category="matter_opening",
        ),
    },
    {
        "id": "4",
        "name": "Timeout after matter creation",
        "description": "INT-2404 has an ambiguous commit; lookup-before-retry prevents a duplicate matter.",
        "expected": "awaiting_approval",
        "required_control": "safe-recovery",
        "approval_test": "none",
        "ticket": Ticket(
            id="4",
            subject="Unknown result for INT-2404",
            body="The matter-opening request INT-2404 timed out. Please retry it so the lawyer can begin work.",
            requester="lawyer.331@example.test",
            requester_role="Lawyer",
            category="matter_opening",
        ),
    },
    {
        "id": "5",
        "name": "Restricted matter access request",
        "description": "A lawyer requests MAT-RESTRICTED-01; the information-barrier owner retains authority.",
        "expected": "blocked",
        "required_control": "information-barrier",
        "approval_test": "block",
        "ticket": Ticket(
            id="5",
            subject="Access needed to MAT-RESTRICTED-01",
            body="Please add me to MAT-RESTRICTED-01. I need to review the documents this afternoon.",
            requester="associate.general@example.test",
            requester_role="Associate",
            category="matter_access",
        ),
    },
    {
        "id": "6",
        "name": "Document add-in unavailable",
        "description": "A general IT issue uses a safe knowledge path without collecting document content or credentials.",
        "expected": "awaiting_approval",
        "required_control": "data-minimisation",
        "approval_test": "none",
        "ticket": Ticket(
            id="6",
            subject="Document save option missing in Word",
            body="The document-management save option has disappeared from Word. I can still work locally but cannot file my document.",
            requester="lawyer.general@example.test",
            requester_role="Lawyer",
            category="general_it",
        ),
    },
]


def seed_demo_tickets(adapter: MemoryTicketAdapter) -> None:
    adapter.tickets.clear()
    adapter.notes.clear()
    adapter.replies.clear()
    for scenario in SCENARIOS:
        adapter.seed(scenario["ticket"])


def scenario_summaries() -> list[dict]:
    return [
        {
            **{key: value for key, value in scenario.items() if key != "ticket"},
            "category": scenario["ticket"].category,
        }
        for scenario in SCENARIOS
    ]

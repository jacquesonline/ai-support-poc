import asyncio

import pytest
from fastapi.testclient import TestClient

from app.ai import FakeDecisionProvider
from app.business import MatterOpeningControlRoom
from app.demo import seed_demo_tickets
from app.improvement import SupportImprovementService
from app.main import ai, app, harvey, improvement, memory, service
from app.policy import PolicyEngine
from app.service import AutomationService
from app.tickets import MemoryTicketAdapter


@pytest.fixture(autouse=True)
def reset_demo_state():
    service.reset()
    improvement.reset()
    harvey.reset()
    ai.activate_prompt(improvement.active_version, improvement.prompt_text())
    seed_demo_tickets(memory)


def test_approved_matter_opening_requires_named_authority():
    client = TestClient(app)
    investigated = client.post("/tickets/1/investigate")
    assert investigated.status_code == 200
    assert investigated.json()["state"] == "awaiting_approval"
    assert investigated.json()["decision"]["proposed_action"]["action_type"] == "process_matter"
    assert "1" not in memory.replies
    approved = client.post("/tickets/1/approval", json={"approved": True, "approved_by": "support.owner"})
    assert approved.status_code == 200
    assert approved.json()["state"] == "executed"
    assert approved.json()["result"]["status"] == "CREATED"
    assert len(memory.replies["1"]) == 1
    assert approved.json()["audit"][-1]["event"] == "authorised_support_action_executed"


def test_rejection_has_no_matter_or_reply_side_effect():
    client = TestClient(app)
    client.post("/tickets/1/investigate")
    rejected = client.post("/tickets/1/approval", json={"approved": False, "approved_by": "support.owner"})
    assert rejected.json()["state"] == "rejected"
    assert "INT-2401" not in service.matters.records
    assert "1" not in memory.replies


def test_replay_reconciles_existing_matter_without_duplicate_create():
    client = TestClient(app)
    investigated = client.post("/tickets/2/investigate").json()
    assert investigated["state"] == "awaiting_approval"
    assert investigated["decision"]["proposed_action"]["action_type"] == "reconcile_existing"
    approved = client.post("/tickets/2/approval", json={"approved": True, "approved_by": "support.owner"}).json()
    assert approved["result"]["status"] == "IDEMPOTENT"
    assert approved["result"]["matter_id"] == "ADT-9002"
    assert len(service.matters.records) == 1


def test_unmapped_office_stops_before_provider_and_cannot_be_approved():
    client = TestClient(app)
    case = client.post("/tickets/3/investigate").json()
    assert case["state"] == "blocked"
    assert case["decision"] is None
    assert case["metrics"]["model_calls"] == 0
    assert any(item["control_id"] == "office-reference" for item in case["controls"])
    assert "reference-data owner" in case["open_questions"][0]["owner"]
    assert client.post("/tickets/3/approval", json={"approved": True, "approved_by": "support.owner"}).status_code == 409


def test_timeout_recovery_uses_lookup_before_retry():
    client = TestClient(app)
    case = client.post("/tickets/4/investigate").json()
    assert case["state"] == "awaiting_approval"
    assert case["decision"]["proposed_action"]["action_type"] == "lookup_before_retry"
    assert any(item["control_id"] == "safe-recovery" for item in case["controls"])
    approved = client.post("/tickets/4/approval", json={"approved": True, "approved_by": "support.owner"}).json()
    assert approved["result"]["status"] == "RECOVERED"
    assert approved["result"]["attempts"] == 1


def test_restricted_matter_access_remains_with_information_barrier_owner():
    client = TestClient(app)
    case = client.post("/tickets/5/investigate").json()
    assert case["state"] == "blocked"
    assert case["decision"] is None
    assert case["metrics"]["model_calls"] == 0
    assert any(item["control_id"] == "information-barrier" for item in case["controls"])
    assert "Information barriers team" == case["open_questions"][0]["owner"]
    assert client.post("/tickets/5/approval", json={"approved": True, "approved_by": "support.owner"}).status_code == 409


def test_general_it_guidance_minimises_legal_document_data():
    client = TestClient(app)
    case = client.post("/tickets/6/investigate").json()
    assert case["state"] == "awaiting_approval"
    assert case["decision"]["intent"] == "general_it"
    assert any(item["control_id"] == "data-minimisation" and item["status"] == "pass" for item in case["controls"])
    message = case["decision"]["proposed_action"]["professional_message"]
    assert "Do not send document content or credentials" in message


def test_demo_contract_is_legal_support_and_self_contained():
    client = TestClient(app)
    page = client.get("/")
    assert page.status_code == 200
    assert "ABL Legal Technology AI Demonstration" in page.text
    chooser = client.get("/workbench")
    assert chooser.status_code == 200
    assert "Choose a proof point" in chooser.text
    assert all(f'/proofs/{name}' in chooser.text for name in ("matter", "support", "harvey", "improvement", "value"))
    full_workbench = client.get("/workbench/full")
    assert full_workbench.status_code == 200
    assert "Choose a case" in full_workbench.text
    brief = client.get("/demo/brief").json()
    assert "ABL-style" in brief["boundary"]
    assert "not abl" in brief["boundary"].lower()
    assert len(client.get("/demo/scenarios").json()) == 6
    assert {item["category"] for item in client.get("/demo/scenarios").json()} == {
        "matter_opening", "matter_access", "general_it"
    }


def test_each_cio_proof_point_has_a_separate_narrative_page():
    client = TestClient(app)
    expected = {
        "matter": "The matter is approved",
        "support": "Turn tickets into",
        "harvey": "Turn a Harvey idea",
        "improvement": "Harvest what works",
        "value": "Put ethics and economics",
    }
    overview = client.get("/").text
    for route, heading in expected.items():
        assert f'/proofs/{route}' in overview
        page = client.get(f"/proofs/{route}")
        assert page.status_code == 200
        assert heading in page.text
        assert 'class="decision-card"' in page.text
        assert "Kris" not in page.text
    assert client.get("/proofs/unknown").status_code == 404


def test_presenter_cheat_sheet_covers_narrative_system_proof_and_release_rules():
    page = TestClient(app).get("/cheatsheet")
    assert page.status_code == 200
    for phrase in (
        "What I identified",
        "What I designed",
        "What I implemented",
        "What the working system does",
        "What evidence it produces",
        "My operating model and release rules",
        "Matter-opening proof",
        "Release rules",
    ):
        assert phrase in page.text


def test_public_pages_share_the_abl_inspired_brand_system():
    client = TestClient(app)
    for route in ("/", "/workbench", "/cheatsheet", "/proofs/matter", "/proofs/value"):
        page = client.get(route)
        assert page.status_code == 200
        assert '/static/brand.css' in page.text
    css = client.get("/static/brand.css").text
    assert "--abl-charcoal" in css
    assert "--abl-font-display" in css
    assert "--abl-space-6" in css
    assert "not an official ABL brand guide" in css


def test_scorecard_reconciles_actions_safe_stops_and_provider_use():
    client = TestClient(app)
    client.post("/tickets/1/investigate")
    client.post("/tickets/1/approval", json={"approved": True, "approved_by": "support.owner"})
    client.post("/tickets/3/investigate")
    client.post("/tickets/5/investigate")
    client.post("/tickets/6/investigate")
    scorecard = client.get("/demo/scorecard").json()
    assert scorecard["runs"] == 4
    assert scorecard["executed"] == 1
    assert scorecard["blocked_or_clarified"] == 2
    assert scorecard["model_calls"] == 2
    assert scorecard["unauthorised_actions"] == 0


def test_experiment_call_cap_stops_repeated_provider_use():
    tickets = MemoryTicketAdapter()
    seed_demo_tickets(tickets)
    local = AutomationService(
        tickets, MatterOpeningControlRoom(), FakeDecisionProvider(), PolicyEngine(), experiment_model_call_cap=1
    )
    first = asyncio.run(local.investigate("1"))
    second = asyncio.run(local.investigate("2"))
    assert first.state == "awaiting_approval"
    assert second.state == "blocked"
    assert second.metrics.model_calls == 0
    assert second.controls[0].control_id == "model-call-cap"


def test_unknown_live_model_cost_blocks_matter_action():
    class UnknownCostProvider(FakeDecisionProvider):
        def decide(self, ticket, context):
            result = super().decide(ticket, context)
            result.provider = "openai"
            result.estimated_cost_aud = None
            return result

    tickets = MemoryTicketAdapter()
    seed_demo_tickets(tickets)
    local = AutomationService(tickets, MatterOpeningControlRoom(), UnknownCostProvider(), PolicyEngine())
    case = asyncio.run(local.investigate("1"))
    assert case.state == "blocked"
    assert any(item.control_id == "experiment-spend" and item.status == "block" for item in case.controls)


def test_improvement_is_anchored_in_six_legal_support_cases():
    client = TestClient(app)
    overview = client.get("/improvement/overview").json()
    assert overview["active_version"] == "1.0.0"
    assert len(overview["evaluation_cases"]) == 6
    assert {item["required_control"] for item in overview["evaluation_cases"]} >= {
        "stable-intake-id", "safe-recovery", "information-barrier", "data-minimisation"
    }
    assert all("legal-support" in item["path"] or "support-investigation" in item["path"] for item in overview["reuse"])


def test_six_case_regression_proves_quality_efficiency_and_authority():
    client = TestClient(app)
    run = client.post("/improvement/evaluate").json()
    assert run["recommendation"] == "activate_candidate"
    assert run["status"] == "awaiting_approval"
    assert run["active"]["passed_cases"] == 6
    assert run["candidate"]["passed_cases"] == 6
    assert run["active"]["model_calls"] == 4
    assert run["candidate"]["model_calls_avoided"] == 2
    assert run["candidate"]["prompt_token_proxy"] < run["active"]["prompt_token_proxy"]
    assert run["candidate"]["actual_model_spend_aud"] == 0
    assert run["candidate"]["unauthorised_actions"] == 0
    assert all(item["passed"] for item in run["candidate"]["cases"])


def test_candidate_activation_requires_named_decision_and_changes_runtime_version():
    client = TestClient(app)
    client.post("/improvement/evaluate")
    assert client.post("/improvement/decision", json={"approved": True, "approved_by": ""}).status_code == 422
    approved = client.post(
        "/improvement/decision",
        json={"approved": True, "approved_by": "legal.support.owner", "note": "Six cases reviewed"},
    )
    assert approved.status_code == 200
    assert client.get("/improvement/overview").json()["active_version"] == "1.1.0"
    case = client.post("/tickets/1/investigate").json()
    proposal = next(item for item in case["audit"] if item["event"] == "proposal_generated")
    assert "1.1.0" in proposal["actor"]


def test_rejected_candidate_keeps_active_legal_support_prompt():
    client = TestClient(app)
    client.post("/improvement/evaluate")
    rejected = client.post(
        "/improvement/decision", json={"approved": False, "approved_by": "legal.support.owner"}
    )
    assert rejected.status_code == 200
    assert client.get("/improvement/overview").json()["active_version"] == "1.0.0"


def test_legal_support_regression_has_hard_provider_call_cap():
    local = SupportImprovementService(improvement.project_root, evaluation_model_call_cap=7)
    with pytest.raises(ValueError, match="above the 7-call review cap"):
        asyncio.run(local.evaluate())


def test_harvey_context_is_public_but_use_cases_are_explicitly_synthetic():
    client = TestClient(app)
    overview = client.get("/harvey/overview").json()
    assert "agreement with Harvey" in overview["public_context"]["statement"]
    assert "synthetic operating hypotheses" in overview["public_context"]["boundary"]
    assert "private Harvey configuration" in overview["public_context"]["boundary"]
    assert len(overview["use_cases"]) == 4
    assert {item["primary_users"] for item in overview["use_cases"]}


def test_harvey_proof_opens_a_dedicated_workflow_demonstrator():
    client = TestClient(app)
    proof = client.get("/proofs/harvey")
    assert 'href="/harvey-demo"' in proof.text
    assert "Demonstrate a Harvey workflow" in proof.text

    demo = client.get("/harvey-demo")
    assert demo.status_code == 200
    assert "Harvey use-case demonstrator" in demo.text
    assert "no Harvey API call" in demo.text
    assert 'id="case-buttons"' in demo.text
    assert 'id="assess-button"' in demo.text
    assert '/static/brand.css' in demo.text


def test_harvey_readiness_review_proves_pilot_design_without_claiming_outcomes():
    client = TestClient(app)
    run = client.post("/harvey/evaluate").json()
    assert run["synthetic"] is True
    assert run["status"] == "pilot_design_ready"
    assert run["readiness"]["use_cases_ready_for_controlled_pilot"] == 4
    assert run["readiness"]["source_contracts_required"] == 4
    assert run["readiness"]["lawyer_review_gates"] == 4
    assert run["readiness"]["autonomous_legal_actions"] == 0
    assert run["readiness"]["real_outcome_evidence_available"] is False
    assert run["economics"]["realised_profit_impact_aud"] is None
    assert "does not prove that Harvey improves quality" in run["evidence_boundary"]
    assert "not predict or attribute a court result" in run["court_outcome_boundary"]


def test_reset_clears_harvey_evaluation_evidence():
    client = TestClient(app)
    client.post("/harvey/evaluate")
    assert client.get("/harvey/overview").json()["last_run"] is not None
    reset = client.post("/demo/seed")
    assert reset.json()["harvey_runs"] == 0
    assert client.get("/harvey/overview").json()["last_run"] is None

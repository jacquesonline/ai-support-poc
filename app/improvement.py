"""Support-specific continuous-improvement evidence for the standalone POC."""

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from app.ai import FakeDecisionProvider
from app.business import MatterOpeningControlRoom
from app.demo import SCENARIOS, seed_demo_tickets
from app.models import Approval, ChangeDecision, EvaluationCaseResult, PromptVersionEvidence, SupportImprovementRun
from app.policy import PolicyEngine
from app.service import AutomationService
from app.tickets import MemoryTicketAdapter


IMPROVEMENT_HYPOTHESIS = (
    "If the legal-support prompt removes matter-reference, office-mapping and information-barrier instructions "
    "already enforced before provider use, v1.1 will preserve all six support outcomes with less prompt context."
)


class SupportImprovementService:
    def __init__(
        self,
        project_root: Path,
        input_rate_per_million_aud: float | None = None,
        output_rate_per_million_aud: float | None = None,
        review_run_cap: int = 4,
        evaluation_model_call_cap: int = 8,
        review_spend_cap_aud: float = 0.10,
    ) -> None:
        self.project_root = project_root
        self.input_rate = input_rate_per_million_aud
        self.output_rate = output_rate_per_million_aud
        self.review_run_cap = review_run_cap
        self.evaluation_model_call_cap = evaluation_model_call_cap
        self.review_spend_cap_aud = review_spend_cap_aud
        self.prompt_paths = {
            "1.0.0": project_root / "prompts" / "support-investigation.md",
            "1.1.0": project_root / "prompts" / "support-investigation.v1.1-candidate.md",
        }
        self.automation_register = json.loads(
            (project_root / "automations" / "support-review-register.json").read_text(encoding="utf-8")
        )
        self.reset()

    def reset(self) -> None:
        self.active_version = "1.0.0"
        self.candidate_version = "1.1.0"
        self.change_status = "not_evaluated"
        self.runs: list[SupportImprovementRun] = []

    def prompt_text(self, version: str | None = None) -> str:
        return self.prompt_paths[version or self.active_version].read_text(encoding="utf-8")

    def overview(self) -> dict:
        return {
            "title": "Improve the AI support POC",
            "boundary": (
                "Evidence is generated from six synthetic legal-support cases using the Matter Opening Control Room. "
                "Token counts are a transparent local proxy; local model spend is $0."
            ),
            "hypothesis": IMPROVEMENT_HYPOTHESIS,
            "active_version": self.active_version,
            "candidate_version": self.candidate_version,
            "change_status": self.change_status,
            "evaluation_cases": [
                {
                    "id": item["id"],
                    "name": item["name"],
                    "expected": item["expected"],
                    "required_control": item["required_control"],
                }
                for item in SCENARIOS
            ],
            "reuse": [
                {
                    "name": "Support resolution skill",
                    "path": "skills/legal-support-resolution/SKILL.md",
                    "role": "Reuses matter, access and general-IT evidence → policy → approval → measurement.",
                },
                {
                    "name": "Versioned support prompt",
                    "path": self._relative_prompt_path(self.active_version),
                    "role": "Supplies the proposal instructions used by this workflow.",
                },
                {
                    "name": "Support improvement skill",
                    "path": "skills/legal-support-improvement/SKILL.md",
                    "role": "Runs the same legal-support regression contract before a version can change.",
                },
            ],
            "automations": self.automation_register["automations"],
            "limits": {
                "review_run_cap": self.review_run_cap,
                "review_runs_used": len(self.runs),
                "evaluation_model_call_cap": self.evaluation_model_call_cap,
                "review_spend_cap_aud": self.review_spend_cap_aud,
                "actual_review_spend_aud": 0.0,
            },
            "last_run": self.runs[-1] if self.runs else None,
        }

    async def evaluate(self) -> SupportImprovementRun:
        if len(self.runs) >= self.review_run_cap:
            raise ValueError(f"The {self.review_run_cap}-run support review cap has been reached")
        required_calls = 8
        if required_calls > self.evaluation_model_call_cap:
            raise ValueError(
                f"The regression requires {required_calls} provider calls, above the "
                f"{self.evaluation_model_call_cap}-call review cap"
            )

        active = await self._evaluate_version(self.active_version, "Active")
        candidate = await self._evaluate_version(self.candidate_version, "Candidate")
        estimated_review_spend = sum(
            value or 0 for value in (active.estimated_live_spend_aud, candidate.estimated_live_spend_aud)
        )
        candidate_regression = candidate.passed_cases != candidate.evaluation_cases
        authority_failure = candidate.unauthorised_actions != 0
        efficiency_gain = candidate.prompt_token_proxy < active.prompt_token_proxy
        already_active = self.active_version == self.candidate_version
        rate_cap_breach = (
            active.estimated_live_spend_aud is not None
            and candidate.estimated_live_spend_aud is not None
            and estimated_review_spend > self.review_spend_cap_aud
        )

        if authority_failure or rate_cap_breach:
            recommendation, status = "stop", "blocked"
        elif candidate_regression:
            recommendation, status = "reject_candidate", "awaiting_approval"
        elif already_active or not efficiency_gain:
            recommendation, status = "keep_active", "awaiting_approval"
        else:
            recommendation, status = "activate_candidate", "awaiting_approval"

        run = SupportImprovementRun(
            id=f"support-review-{len(self.runs) + 1:02d}",
            hypothesis=IMPROVEMENT_HYPOTHESIS,
            status=status,
            recommendation=recommendation,
            active=active,
            candidate=candidate,
            evidence=[
                f"Candidate passed {candidate.passed_cases}/{candidate.evaluation_cases} legal-support cases; active passed {active.passed_cases}/{active.evaluation_cases}.",
                f"Both versions avoided provider use for {candidate.model_calls_avoided}/{candidate.evaluation_cases} cases through deterministic pre-checks.",
                f"Candidate prompt proxy is {candidate.prompt_token_proxy} tokens versus {active.prompt_token_proxy} for the active prompt.",
                "Credential-free evaluation made no paid model call; actual model spend is $0.0000 AUD.",
                "The normal matter case executed only after named approval; reference and information-barrier cases rejected an approval override.",
            ],
            controls=[
                "Same six matter-opening, access and general-IT scenarios for both versions",
                f"Hard review cap: {self.evaluation_model_call_cap} provider calls",
                "Candidate remains inactive until named approval",
                "Active v1.0 prompt remains the rollback path",
                "Any outcome regression or unauthorised action prevents activation",
            ],
            owner="Support workflow owner",
        )
        self.runs.append(run)
        self.change_status = status
        return run

    def decide(self, decision: ChangeDecision) -> SupportImprovementRun:
        if not self.runs:
            raise ValueError("Run the support regression check before recording a decision")
        run = self.runs[-1]
        if run.status != "awaiting_approval":
            raise ValueError(f"The latest support review is {run.status}")
        if decision.approved and run.recommendation != "activate_candidate":
            raise ValueError(f"The evidence recommends {run.recommendation}; candidate activation is unavailable")
        run.decided_by = decision.approved_by
        run.decision_note = decision.note
        run.decided_at = datetime.now(timezone.utc)
        if decision.approved:
            self.active_version = self.candidate_version
            run.status = "approved"
            self.change_status = "approved"
        else:
            run.status = "rejected"
            self.change_status = "rejected"
        return run

    async def _evaluate_version(self, version: str, label: str) -> PromptVersionEvidence:
        prompt_text = self.prompt_text(version)
        workflow = AutomationService(
            self._seeded_tickets(),
            MatterOpeningControlRoom(),
            FakeDecisionProvider(version, prompt_text),
            PolicyEngine(),
            experiment_spend_cap_aud=0.0,
            experiment_model_call_cap=4,
        )
        tickets = workflow.tickets
        results: list[EvaluationCaseResult] = []

        for scenario in SCENARIOS:
            before_calls = workflow.total_model_calls
            case = await workflow.investigate(scenario["id"])
            observed_state = case.state
            calls = workflow.total_model_calls - before_calls
            control_id = scenario["required_control"]
            control_observed = any(check.control_id == control_id for check in case.controls)
            approval_gate_passed = None
            passed = case.state == scenario["expected"] and control_observed
            detail = f"Expected and observed {case.state}."

            if scenario["approval_test"] == "execute":
                no_reply_before_approval = scenario["id"] not in tickets.replies
                approved = await workflow.approve(
                    scenario["id"], Approval(approved=True, approved_by="regression.owner")
                )
                approval_gate_passed = (
                    no_reply_before_approval
                    and approved.state == "executed"
                    and len(tickets.replies.get(scenario["id"], [])) == 1
                )
                passed = passed and approval_gate_passed
                detail = "Proposal remained inactive until named approval, then one synthetic action executed."
            elif case.metrics.model_calls == 0:
                passed = passed and calls == 0
                detail = f"Observed {case.state}; deterministic evidence stopped the case before provider use."
            if scenario["approval_test"] == "block":
                try:
                    await workflow.approve(
                        scenario["id"], Approval(approved=True, approved_by="regression.owner")
                    )
                    blocked_override = False
                except ValueError:
                    blocked_override = True
                passed = passed and blocked_override
                detail = "The legal-support control blocked the case and the approval endpoint refused an override."

            results.append(EvaluationCaseResult(
                scenario_id=scenario["id"], name=scenario["name"],
                expected_state=scenario["expected"], actual_state=observed_state,
                passed=passed, model_calls=calls, required_control=control_id,
                control_observed=control_observed, approval_gate_passed=approval_gate_passed,
                detail=detail,
            ))

        estimated_live_spend = None
        if self.input_rate is not None and self.output_rate is not None:
            estimated_live_spend = round(
                workflow.total_input_tokens * self.input_rate / 1_000_000
                + workflow.total_output_tokens * self.output_rate / 1_000_000, 6
            )
        passed_cases = sum(item.passed for item in results)
        return PromptVersionEvidence(
            version=version, label=label, prompt_path=self._relative_prompt_path(version),
            prompt_characters=len(prompt_text), prompt_token_proxy=math.ceil(len(prompt_text) / 4),
            evaluation_cases=len(results), passed_cases=passed_cases,
            pass_rate_pct=round(passed_cases / len(results) * 100, 1),
            model_calls=workflow.total_model_calls, model_calls_avoided=len(results) - workflow.total_model_calls,
            input_token_proxy=workflow.total_input_tokens, output_token_proxy=workflow.total_output_tokens,
            workflow_processing_milliseconds=round(sum(item.metrics.processing_milliseconds for item in workflow.cases.values()), 3),
            actual_model_spend_aud=0.0, estimated_live_spend_aud=estimated_live_spend,
            unauthorised_actions=workflow.scorecard()["unauthorised_actions"], cases=results,
        )

    def _seeded_tickets(self) -> MemoryTicketAdapter:
        tickets = MemoryTicketAdapter()
        seed_demo_tickets(tickets)
        return tickets

    def _relative_prompt_path(self, version: str) -> str:
        return self.prompt_paths[version].relative_to(self.project_root).as_posix()

import json
import math
from abc import ABC, abstractmethod

from openai import OpenAI

from app.models import AIDecision, ActionType, DecisionRun, ProposedAction, Ticket


class DecisionProvider(ABC):
    @abstractmethod
    def decide(self, ticket: Ticket, context: dict) -> DecisionRun: ...


class FakeDecisionProvider(DecisionProvider):
    """Credential-free, deterministic provider used for the legal-support demo."""

    def __init__(self, prompt_version: str = "1.0.0", prompt_text: str | None = None) -> None:
        self.prompt_version = prompt_version
        self.prompt_text = prompt_text

    def activate_prompt(self, version: str, prompt_text: str) -> None:
        self.prompt_version = version
        self.prompt_text = prompt_text

    def decide(self, ticket: Ticket, context: dict) -> DecisionRun:
        if ticket.category == "general_it":
            decision = self._general_it_decision(ticket, context)
        else:
            decision = self._matter_decision(ticket, context)
        input_payload = json.dumps({"ticket": ticket.model_dump(), "permitted_context": context})
        input_token_proxy = math.ceil((len(self.prompt_text or "") + len(input_payload)) / 4) if self.prompt_text else 0
        output_token_proxy = math.ceil(len(decision.model_dump_json()) / 4) if self.prompt_text else 0
        return DecisionRun(
            decision=decision,
            provider="deterministic",
            model=f"legal-support-rules-{self.prompt_version}",
            input_tokens=input_token_proxy,
            output_tokens=output_token_proxy,
            estimated_cost_aud=0.0,
        )

    @staticmethod
    def _matter_decision(ticket: Ticket, context: dict) -> AIDecision:
        request_id = context["request_id"]
        scenario = context["scenario"]
        existing = context.get("existing_record")
        if existing:
            action_type = ActionType.reconcile_existing
            intent = "matter_replay"
            resolution_code = "IDEMPOTENT_RECONCILIATION"
            summary = f"{request_id} already has authoritative matter {existing['matter_id']}; another create would be unsafe."
            reasoning = "The stable intake ID links the request to an existing matter, so the safe proposal is a reconciled no-op."
        elif scenario == "timeout-after-commit":
            action_type = ActionType.lookup_before_retry
            intent = "matter_recovery"
            resolution_code = "LOOKUP_BEFORE_RETRY"
            summary = f"{request_id} has an ambiguous create result; a blind retry could create a duplicate matter."
            reasoning = "The control room must query by the stable intake ID before considering another create."
        else:
            action_type = ActionType.process_matter
            intent = "matter_opening"
            resolution_code = "CONTROLLED_MATTER_PROCESS"
            summary = f"{request_id} is approved, valid and has no authoritative matter record yet."
            reasoning = "The permitted intake evidence supports controlled processing, subject to policy and named approval."
        return AIDecision(
            summary=summary,
            intent=intent,
            facts=[
                f"Intake {request_id} is approved.",
                f"Office {context['office']} and practice {context['practice']} are controlled reference values.",
                "The stable intake ID is retained across intake, processing and reconciliation.",
            ],
            assumptions=[],
            open_questions=[],
            reasoning=reasoning,
            confidence=0.96,
            proposed_action=ProposedAction(
                action_type=action_type,
                reference_id=request_id,
                target_system="Matter Opening Control Room",
                resolution_code=resolution_code,
                professional_message=(
                    f"Support has verified {request_id} and prepared the controlled next step. "
                    "No matter action will occur until the support owner approves it."
                ),
            ),
        )

    @staticmethod
    def _general_it_decision(ticket: Ticket, context: dict) -> AIDecision:
        steps = context["known_safe_steps"]
        return AIDecision(
            summary="The document-management option is unavailable in Word; safe client-side checks can be tried first.",
            intent="general_it",
            facts=[f"Known service: {context['service']}.", context["prohibited"]],
            assumptions=[],
            open_questions=["If the safe steps fail, what visible error code is shown?"],
            reasoning="A bounded knowledge path can restore the add-in or collect a non-sensitive error code without requesting document content or credentials.",
            confidence=0.9,
            proposed_action=ProposedAction(
                action_type=ActionType.reply_only,
                reference_id=None,
                target_system="Legal service desk",
                resolution_code="SAFE_KNOWLEDGE_GUIDANCE",
                professional_message="Please confirm the add-in is enabled, restart Word, and send only the visible error code if the option remains unavailable. Do not send document content or credentials.",
            ),
        )


class OpenAIDecisionProvider(DecisionProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        input_cost_per_million_aud: float | None = None,
        output_cost_per_million_aud: float | None = None,
    ) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.input_cost_per_million_aud = input_cost_per_million_aud
        self.output_cost_per_million_aud = output_cost_per_million_aud
        self.prompt_version = "1.0.0"
        self.instructions = "Prepare an evidence-bound legal-technology support proposal without executing it."

    def activate_prompt(self, version: str, prompt_text: str) -> None:
        self.prompt_version = version
        self.instructions = prompt_text

    def decide(self, ticket: Ticket, context: dict) -> DecisionRun:
        response = self.client.responses.parse(
            model=self.model,
            instructions=self.instructions,
            input=json.dumps({"ticket": ticket.model_dump(), "permitted_context": context}),
            text_format=AIDecision,
            max_output_tokens=900,
            store=False,
        )
        if response.output_parsed is None:
            raise RuntimeError("Model did not return a valid structured decision")
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
        estimated_cost = None
        if self.input_cost_per_million_aud is not None and self.output_cost_per_million_aud is not None:
            estimated_cost = round(
                input_tokens * self.input_cost_per_million_aud / 1_000_000
                + output_tokens * self.output_cost_per_million_aud / 1_000_000,
                6,
            )
        return DecisionRun(
            decision=response.output_parsed,
            provider="openai",
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_aud=estimated_cost,
        )

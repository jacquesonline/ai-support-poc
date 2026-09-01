from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    process_matter = "process_matter"
    reconcile_existing = "reconcile_existing"
    lookup_before_retry = "lookup_before_retry"
    route_reference_exception = "route_reference_exception"
    route_access_request = "route_access_request"
    reply_only = "reply_only"
    request_information = "request_information"


class ControlStatus(str, Enum):
    passed = "pass"
    review = "review"
    blocked = "block"


class Ticket(BaseModel):
    id: str
    subject: str
    body: str
    requester: str
    requester_role: str
    category: Literal["matter_opening", "matter_access", "general_it"]
    status: str = "open"


class ProposedAction(BaseModel):
    action_type: ActionType
    reference_id: str | None = None
    target_system: str
    resolution_code: str
    professional_message: str


class AIDecision(BaseModel):
    summary: str
    intent: Literal[
        "matter_opening",
        "matter_replay",
        "matter_recovery",
        "matter_access",
        "general_it",
        "unclear",
    ]
    facts: list[str]
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    reasoning: str
    confidence: float = Field(ge=0, le=1)
    proposed_action: ProposedAction


class DecisionRun(BaseModel):
    decision: AIDecision
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_aud: float | None = None


class EvidenceItem(BaseModel):
    source: str
    claim: str
    status: Literal["confirmed", "missing", "conflict"]


class OpenQuestion(BaseModel):
    question: str
    owner: str
    blocks_action: bool = True


class ControlCheck(BaseModel):
    control_id: str
    label: str
    status: ControlStatus
    detail: str


class RunMetrics(BaseModel):
    baseline_handling_minutes: float = 15.0
    processing_milliseconds: float = 0
    human_review_minutes: float = 0
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_model_cost_aud: float | None = None
    retry_count: int = 0
    material_correction: bool = False


class AuditEvent(BaseModel):
    event: str
    actor: str
    detail: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Approval(BaseModel):
    approved: bool
    approved_by: str = Field(min_length=1)
    note: str | None = None
    review_minutes: float = Field(default=1.5, ge=0)
    material_correction: bool = False


class CaseRecord(BaseModel):
    ticket: Ticket
    hypothesis: str
    decision: AIDecision | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    controls: list[ControlCheck] = Field(default_factory=list)
    policy_reasons: list[str] = Field(default_factory=list)
    requires_approval: bool = True
    state: Literal[
        "needs_clarification",
        "awaiting_approval",
        "blocked",
        "approved",
        "rejected",
        "executed",
    ] = "awaiting_approval"
    result: dict[str, Any] | None = None
    metrics: RunMetrics = Field(default_factory=RunMetrics)
    audit: list[AuditEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangeDecision(BaseModel):
    approved: bool
    approved_by: str = Field(min_length=1)
    note: str | None = None


class EvaluationCaseResult(BaseModel):
    scenario_id: str
    name: str
    expected_state: str
    actual_state: str
    passed: bool
    model_calls: int
    required_control: str
    control_observed: bool
    approval_gate_passed: bool | None = None
    detail: str


class PromptVersionEvidence(BaseModel):
    version: str
    label: str
    prompt_path: str
    prompt_characters: int
    prompt_token_proxy: int
    evaluation_cases: int
    passed_cases: int
    pass_rate_pct: float
    model_calls: int
    model_calls_avoided: int
    input_token_proxy: int
    output_token_proxy: int
    workflow_processing_milliseconds: float
    actual_model_spend_aud: float
    estimated_live_spend_aud: float | None = None
    unauthorised_actions: int
    cases: list[EvaluationCaseResult]


class SupportImprovementRun(BaseModel):
    id: str
    hypothesis: str
    status: Literal["awaiting_approval", "approved", "rejected", "blocked"]
    recommendation: Literal["activate_candidate", "keep_active", "reject_candidate", "stop"]
    active: PromptVersionEvidence
    candidate: PromptVersionEvidence
    evidence: list[str]
    controls: list[str]
    owner: str
    decision_note: str | None = None
    decided_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: datetime | None = None

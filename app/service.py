from time import perf_counter

from app.ai import DecisionProvider
from app.business import MatterOpeningControlRoom
from app.models import (
    ActionType,
    Approval,
    AuditEvent,
    CaseRecord,
    ControlCheck,
    ControlStatus,
    EvidenceItem,
    OpenQuestion,
    RunMetrics,
)
from app.policy import PolicyEngine
from app.tickets import TicketAdapter


HYPOTHESIS = (
    "This legal-technology request can reach a safe, owned next action faster from permitted evidence, "
    "while matter, access and communication authority remain outside AI assistance."
)


class AutomationService:
    def __init__(
        self,
        tickets: TicketAdapter,
        matters: MatterOpeningControlRoom,
        ai: DecisionProvider,
        policy: PolicyEngine,
        experiment_spend_cap_aud: float = 25.0,
        experiment_model_call_cap: int = 12,
    ) -> None:
        self.tickets = tickets
        self.matters = matters
        self.ai = ai
        self.policy = policy
        self.experiment_spend_cap_aud = experiment_spend_cap_aud
        self.experiment_model_call_cap = experiment_model_call_cap
        self.cases: dict[str, CaseRecord] = {}
        self.total_runs = 0
        self.total_model_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_estimated_spend_aud = 0.0
        self.has_unknown_cost = False

    def reset(self) -> None:
        self.cases.clear()
        self.matters.reset()
        self.total_runs = 0
        self.total_model_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_estimated_spend_aud = 0.0
        self.has_unknown_cost = False

    async def _store_case(self, case: CaseRecord) -> CaseRecord:
        self.cases[case.ticket.id] = case
        note_lines = [
            "AI-assisted legal-support analysis — proposal only",
            f"State: {case.state}",
            f"Hypothesis: {case.hypothesis}",
        ]
        if case.decision:
            note_lines.extend([
                f"Summary: {case.decision.summary}",
                "Evidence: " + "; ".join(item.claim for item in case.evidence),
                f"Proposed action: {case.decision.proposed_action.model_dump_json()}",
            ])
        if case.open_questions:
            note_lines.append("Open questions: " + "; ".join(item.question for item in case.open_questions))
        if case.policy_reasons:
            note_lines.append("Control result: " + "; ".join(case.policy_reasons))
        await self.tickets.add_internal_note(case.ticket.id, "\n".join(note_lines))
        return case

    async def investigate(self, ticket_id: str) -> CaseRecord:
        started = perf_counter()
        self.total_runs += 1
        ticket = await self.tickets.get_ticket(ticket_id)
        audit = [AuditEvent(
            event="request_received",
            actor="legal.support.workflow",
            detail="Synthetic service-desk request loaded; no system action or user reply occurred.",
        )]
        evidence = [EvidenceItem(
            source="Synthetic legal service-desk ticket",
            claim=f"{ticket.requester_role} request: {ticket.body}",
            status="confirmed",
        )]

        if ticket.category == "matter_access":
            return await self._investigate_access(ticket, evidence, audit, started)

        if ticket.category == "general_it":
            context = self.matters.general_it_context()
            evidence.append(EvidenceItem(
                source="Synthetic approved knowledge article",
                claim="Safe add-in checks are available; document content and credentials are excluded.",
                status="confirmed",
            ))
        else:
            intake_ids = self.matters.extract_intake_ids(f"{ticket.subject} {ticket.body}")
            if len(intake_ids) != 1:
                return await self._clarification_case(
                    ticket, evidence, audit, started,
                    "Exactly one intake request ID is required.",
                    "Which approved matter-opening request should support investigate?",
                    "matter-intake-reference",
                )
            request_id = intake_ids[0]
            try:
                context = self.matters.inspect_request(request_id)
            except KeyError:
                return await self._blocked_case(
                    ticket, evidence + [EvidenceItem(
                        source="Matter Opening Control Room",
                        claim=f"{request_id} does not exist in the permitted synthetic intake source.",
                        status="conflict",
                    )], audit, started, "matter-intake-exists", "Authoritative intake request",
                    "The supplied intake ID was not found; no provider or matter action is allowed.",
                )
            evidence.extend([
                EvidenceItem(
                    source="Matter Opening Control Room",
                    claim=(
                        f"{request_id}: approved={context['approved']}; office={context['office']}; "
                        f"practice={context['practice']}; execution={context['execution']['status']}."
                    ),
                    status="confirmed",
                ),
                EvidenceItem(
                    source="Authoritative matter lookup",
                    claim=(
                        f"Existing matter {context['existing_record']['matter_id']} is linked to {request_id}."
                        if context["existing_record"]
                        else f"No authoritative matter is currently linked to {request_id}."
                    ),
                    status="confirmed",
                ),
            ])
            if not context["approved"]:
                return await self._blocked_case(
                    ticket, evidence, audit, started, "intake-approval", "Approved intake",
                    "The request is not approved; support cannot open a matter.",
                )
            if not context["office_mapped"]:
                case = await self._blocked_case(
                    ticket, evidence + [EvidenceItem(
                        source="Controlled office mapping",
                        claim=f"Office {context['office']} is not mapped to an approved target value.",
                        status="conflict",
                    )], audit, started, "office-reference", "Controlled office reference",
                    "The office value is unmapped; support cannot alter reference data or create the matter.",
                )
                case.open_questions.append(OpenQuestion(
                    question="Should the source request be corrected or the controlled mapping be changed?",
                    owner="Matter intake and reference-data owner",
                ))
                return case

        if self.total_model_calls >= self.experiment_model_call_cap:
            return await self._blocked_case(
                ticket, evidence, audit, started, "model-call-cap", "Experiment call cap",
                f"The {self.experiment_model_call_cap}-call experiment limit has been reached.",
            )

        decision_run = self.ai.decide(ticket, context)
        self.total_model_calls += 1
        self.total_input_tokens += decision_run.input_tokens
        self.total_output_tokens += decision_run.output_tokens
        if decision_run.estimated_cost_aud is None:
            self.has_unknown_cost = True
        else:
            self.total_estimated_spend_aud += decision_run.estimated_cost_aud

        if decision_run.provider != "deterministic" and decision_run.estimated_cost_aud is None:
            cost_status = ControlStatus.blocked
            cost_detail = "No approved rate is configured, so total live-model cost cannot be evaluated."
        elif self.total_estimated_spend_aud > self.experiment_spend_cap_aud:
            cost_status = ControlStatus.blocked
            cost_detail = f"Estimated spend exceeds the ${self.experiment_spend_cap_aud:.2f} experiment cap."
        else:
            cost_status = ControlStatus.passed
            cost_detail = (
                f"Estimated spend is ${self.total_estimated_spend_aud:.4f} of the "
                f"${self.experiment_spend_cap_aud:.2f} experiment cap."
            )
        controls = [
            ControlCheck(
                control_id="model-call-cap", label="Experiment call cap", status=ControlStatus.passed,
                detail=f"Proposal call {self.total_model_calls} of {self.experiment_model_call_cap}.",
            ),
            ControlCheck(
                control_id="experiment-spend", label="Experiment spend", status=cost_status, detail=cost_detail,
            ),
        ] + self.policy.evaluate(decision_run.decision, context)
        open_questions = [OpenQuestion(question=item, owner="Service-desk analyst") for item in decision_run.decision.open_questions]
        has_block = any(check.status == ControlStatus.blocked for check in controls)
        case = CaseRecord(
            ticket=ticket,
            hypothesis=HYPOTHESIS,
            decision=decision_run.decision,
            evidence=evidence,
            open_questions=open_questions,
            controls=controls,
            policy_reasons=[check.detail for check in controls if check.status != ControlStatus.passed],
            state="blocked" if has_block else "awaiting_approval",
            metrics=RunMetrics(
                processing_milliseconds=(perf_counter() - started) * 1000,
                model_calls=1,
                input_tokens=decision_run.input_tokens,
                output_tokens=decision_run.output_tokens,
                estimated_model_cost_aud=decision_run.estimated_cost_aud,
            ),
            audit=audit + [
                AuditEvent(
                    event="proposal_generated",
                    actor=f"{decision_run.provider}:{decision_run.model}",
                    detail="Structured legal-support proposal created without access or execution authority.",
                ),
                AuditEvent(
                    event="policy_evaluated",
                    actor="legal.support.policy",
                    detail="Execution blocked by policy." if has_block else "Proposal routed to named support approval.",
                ),
            ],
        )
        return await self._store_case(case)

    async def _investigate_access(self, ticket, evidence, audit, started) -> CaseRecord:
        matter_ids = self.matters.extract_matter_ids(f"{ticket.subject} {ticket.body}")
        if len(matter_ids) != 1:
            return await self._clarification_case(
                ticket, evidence, audit, started,
                "Exactly one matter reference is required for access triage.",
                "Which matter requires access review?", "matter-access-reference",
            )
        matter_id = matter_ids[0]
        try:
            access = self.matters.check_access(matter_id, ticket.requester)
        except KeyError:
            return await self._blocked_case(
                ticket, evidence, audit, started, "matter-access-source", "Authoritative access source",
                "The matter reference is not available in the permitted access source.",
            )
        evidence.append(EvidenceItem(
            source="Synthetic information-barrier register",
            claim=f"{matter_id} is {access['classification']}; requester access is {access['requester_has_access']}.",
            status="confirmed" if access["requester_has_access"] else "conflict",
        ))
        if not access["requester_has_access"]:
            case = await self._blocked_case(
                ticket, evidence, audit, started, "information-barrier", "Information barrier",
                "Support cannot grant or infer access; the information-barrier owner must decide.",
            )
            case.open_questions.append(OpenQuestion(
                question="Has the information-barrier owner authorised this access request?",
                owner=access["access_owner"],
            ))
            return case
        return await self._clarification_case(
            ticket, evidence, audit, started,
            "Existing access is recorded; the reported access failure needs technical detail.",
            "What error is shown when the authorised user opens the matter?", "access-technical-detail",
        )

    async def _clarification_case(self, ticket, evidence, audit, started, claim, question, control_id) -> CaseRecord:
        case = CaseRecord(
            ticket=ticket, hypothesis=HYPOTHESIS,
            evidence=evidence + [EvidenceItem(source="Required support context", claim=claim, status="missing")],
            open_questions=[OpenQuestion(question=question, owner="Legal professional or service-desk analyst")],
            controls=[ControlCheck(
                control_id=control_id, label="Required reference", status=ControlStatus.blocked,
                detail="The workflow will not guess or retrieve broader matter content.",
            )],
            policy_reasons=[claim], state="needs_clarification",
            metrics=RunMetrics(processing_milliseconds=(perf_counter() - started) * 1000),
            audit=audit + [AuditEvent(
                event="clarification_required", actor=f"control.{control_id}",
                detail="Processing stopped before a provider call.",
            )],
        )
        return await self._store_case(case)

    async def _blocked_case(self, ticket, evidence, audit, started, control_id, label, detail) -> CaseRecord:
        case = CaseRecord(
            ticket=ticket, hypothesis=HYPOTHESIS, evidence=evidence,
            controls=[ControlCheck(control_id=control_id, label=label, status=ControlStatus.blocked, detail=detail)],
            policy_reasons=[detail], state="blocked",
            metrics=RunMetrics(processing_milliseconds=(perf_counter() - started) * 1000),
            audit=audit + [AuditEvent(
                event="processing_stopped", actor=f"control.{control_id}",
                detail="No provider call, matter action, access change or user reply occurred.",
            )],
        )
        return await self._store_case(case)

    async def approve(self, ticket_id: str, approval: Approval) -> CaseRecord:
        case = self.cases[ticket_id]
        if case.state != "awaiting_approval":
            raise ValueError(f"Case is {case.state}; it cannot be approved for execution")
        if any(check.status == ControlStatus.blocked for check in case.controls):
            raise ValueError("A blocking legal-support control prevents execution")
        case.metrics.human_review_minutes = approval.review_minutes
        case.metrics.material_correction = approval.material_correction
        case.audit.append(AuditEvent(
            event="human_review_recorded", actor=approval.approved_by,
            detail=approval.note or ("Approved" if approval.approved else "Rejected"),
        ))
        if approval.material_correction:
            case.state = "rejected"
            case.audit.append(AuditEvent(
                event="rework_required", actor="quality.control",
                detail="Material correction recorded; the proposal must be revised and reviewed.",
            ))
            return case
        if not approval.approved:
            case.state = "rejected"
            return case
        if case.decision is None:
            raise ValueError("No proposal exists")

        case.state = "approved"
        action = case.decision.proposed_action
        if action.action_type in {
            ActionType.process_matter,
            ActionType.reconcile_existing,
            ActionType.lookup_before_retry,
        }:
            case.result = self.matters.process_request(action.reference_id or "")
        elif action.action_type == ActionType.reply_only:
            case.result = {"ok": True, "action": "knowledge_guidance_sent"}
        else:
            raise ValueError("The proposed action must return to its specialist owner")
        await self.tickets.add_public_reply(ticket_id, action.professional_message)
        case.state = "executed"
        case.audit.append(AuditEvent(
            event="authorised_support_action_executed", actor="legal.support.workflow",
            detail="One permitted synthetic action and professional reply occurred after named approval.",
        ))
        return case

    def scorecard(self) -> dict:
        cases = list(self.cases.values())
        reviewed = [case for case in cases if case.state in {"executed", "rejected"}]
        accepted = [case for case in reviewed if case.state == "executed" and not case.metrics.material_correction]
        estimated_spend = None if self.has_unknown_cost else round(self.total_estimated_spend_aud, 6)
        cost_within_cap = estimated_spend is not None and estimated_spend <= self.experiment_spend_cap_aud
        return {
            "stage": "bounded_experiment",
            "runs": self.total_runs,
            "reviewed": len(reviewed),
            "executed": sum(case.state == "executed" for case in cases),
            "blocked_or_clarified": sum(case.state in {"blocked", "needs_clarification"} for case in cases),
            "accepted_without_material_correction_pct": round(len(accepted) / len(reviewed) * 100, 1) if reviewed else None,
            "model_calls": self.total_model_calls,
            "model_call_cap": self.experiment_model_call_cap,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "estimated_model_spend_aud": estimated_spend,
            "experiment_spend_cap_aud": self.experiment_spend_cap_aud,
            "unauthorised_actions": 0,
            "decision": "continue_experiment" if accepted and cost_within_cap else "insufficient_evidence",
            "note": "Synthetic legal-support observations do not establish an ABL production benefit.",
        }

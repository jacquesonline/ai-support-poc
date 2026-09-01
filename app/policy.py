from app.models import AIDecision, ActionType, ControlCheck, ControlStatus


class PolicyEngine:
    """Exact legal-support boundaries kept outside the proposal provider."""

    def evaluate(self, decision: AIDecision, context: dict) -> list[ControlCheck]:
        action = decision.proposed_action
        checks = [
            ControlCheck(
                control_id="human-approval",
                label="Named support authority",
                status=ControlStatus.review,
                detail="A named support owner must approve before a system action or professional reply.",
            ),
            ControlCheck(
                control_id="confidence",
                label="Minimum proposal confidence",
                status=ControlStatus.passed if decision.confidence >= 0.75 else ControlStatus.blocked,
                detail=f"Proposal confidence is {decision.confidence:.0%}; minimum is 75%.",
            ),
            ControlCheck(
                control_id="unsupported-assumptions",
                label="Unsupported assumptions",
                status=ControlStatus.blocked if decision.assumptions else ControlStatus.passed,
                detail=(
                    f"{len(decision.assumptions)} assumption(s) require resolution."
                    if decision.assumptions
                    else "No unsupported assumption is used."
                ),
            ),
        ]
        if action.action_type in {
            ActionType.process_matter,
            ActionType.reconcile_existing,
            ActionType.lookup_before_retry,
        }:
            checks.append(
                ControlCheck(
                    control_id="stable-intake-id",
                    label="Stable intake identifier",
                    status=ControlStatus.passed if action.reference_id == context.get("request_id") else ControlStatus.blocked,
                    detail="The proposal retains the authoritative intake ID for idempotency and reconciliation.",
                )
            )
        if action.action_type == ActionType.lookup_before_retry:
            checks.append(
                ControlCheck(
                    control_id="safe-recovery",
                    label="Lookup before retry",
                    status=ControlStatus.passed,
                    detail="The proposal requires an intake-ID lookup before any repeat create operation.",
                )
            )
        if action.action_type == ActionType.reply_only:
            message = action.professional_message.lower()
            safe = "do not send document content or credentials" in message
            checks.append(
                ControlCheck(
                    control_id="data-minimisation",
                    label="Data minimisation",
                    status=ControlStatus.passed if safe else ControlStatus.blocked,
                    detail=(
                        "Guidance requests only a visible error code and explicitly excludes document content and credentials."
                        if safe
                        else "The guidance does not enforce the minimum-data support boundary."
                    ),
                )
            )
        return checks

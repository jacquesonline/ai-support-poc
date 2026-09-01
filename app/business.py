"""Synthetic legal-technology systems used by the support-desk demonstration."""

import re


class MatterOpeningControlRoom:
    """In-memory version of the synthetic Matter Opening Control Room contract."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.requests = {
            "INT-2401": {
                "client": "Northstar Renewables",
                "matter": "Project Banksia",
                "office": "MEL",
                "practice": "CORP",
                "partner": "P-104",
                "approved": True,
                "scenario": "normal",
            },
            "INT-2402": {
                "client": "Harbour Medical",
                "matter": "Privacy review",
                "office": "SYD",
                "practice": "LIT",
                "partner": "P-218",
                "approved": True,
                "scenario": "duplicate",
            },
            "INT-2403": {
                "client": "Cobalt Logistics",
                "matter": "Fleet acquisition",
                "office": "MEL-X",
                "practice": "CORP",
                "partner": "P-104",
                "approved": True,
                "scenario": "invalid-reference",
            },
            "INT-2404": {
                "client": "Southern Arc",
                "matter": "Employment advice",
                "office": "MEL",
                "practice": "EMP",
                "partner": "P-331",
                "approved": True,
                "scenario": "timeout-after-commit",
            },
        }
        self.records = {
            "INT-2402": {
                "matter_id": "ADT-9002",
                "status": "OPEN",
                "client": "Harbour Medical",
                "matter": "Privacy review",
            }
        }
        self.executions = {request_id: {"status": "QUEUED", "attempts": 0} for request_id in self.requests}
        self.sequence = 9004
        self.restricted_matters = {
            "MAT-RESTRICTED-01": {
                "classification": "Restricted",
                "access_owner": "Information barriers team",
                "members": ["partner.restricted@example.test"],
            }
        }

    @staticmethod
    def extract_intake_ids(text: str) -> list[str]:
        return list(dict.fromkeys(re.findall(r"\bINT-\d{4}\b", text.upper())))

    @staticmethod
    def extract_matter_ids(text: str) -> list[str]:
        return list(dict.fromkeys(re.findall(r"\bMAT-[A-Z0-9-]+\b", text.upper())))

    def inspect_request(self, request_id: str) -> dict:
        request = {"request_id": request_id, **self.requests[request_id]}
        return {
            **request,
            "execution": dict(self.executions[request_id]),
            "existing_record": self.records.get(request_id),
            "office_mapped": request["office"] in {"MEL", "SYD"},
        }

    def check_access(self, matter_id: str, requester: str) -> dict:
        matter = self.restricted_matters[matter_id]
        return {
            "matter_id": matter_id,
            "classification": matter["classification"],
            "access_owner": matter["access_owner"],
            "requester_has_access": requester in matter["members"],
        }

    def process_request(self, request_id: str) -> dict:
        request = self.requests[request_id]
        execution = self.executions[request_id]
        execution["attempts"] += 1
        if not request["approved"] or request["office"] not in {"MEL", "SYD"}:
            execution.update(status="EXCEPTION", detail="Controlled reference-data exception")
            return {"ok": False, "request_id": request_id, **execution}

        existing = self.records.get(request_id)
        if existing:
            execution.update(
                status="IDEMPOTENT",
                matter_id=existing["matter_id"],
                detail="Existing authoritative matter found; duplicate create avoided",
            )
            return {"ok": True, "request_id": request_id, **execution}

        matter_id = f"ADT-{self.sequence}"
        self.sequence += 1
        self.records[request_id] = {
            "matter_id": matter_id,
            "status": "OPEN",
            "client": request["client"],
            "matter": request["matter"],
        }
        if request["scenario"] == "timeout-after-commit":
            execution.update(
                status="RECOVERED",
                matter_id=matter_id,
                detail="Create response timed out; lookup by intake ID confirmed the committed matter",
            )
        else:
            execution.update(status="CREATED", matter_id=matter_id, detail="Matter created and reconciled")
        return {"ok": True, "request_id": request_id, **execution}

    @staticmethod
    def general_it_context() -> dict:
        return {
            "service": "Document-management Office integration",
            "known_safe_steps": [
                "Confirm the document-management add-in is enabled",
                "Restart the Office application",
                "Capture the visible error code without document content",
            ],
            "prohibited": "Do not request privileged document content, credentials or mailbox exports",
        }

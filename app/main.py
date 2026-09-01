from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.ai import FakeDecisionProvider, OpenAIDecisionProvider
from app.business import MatterOpeningControlRoom
from app.config import get_settings
from app.demo import DEMO_BRIEF, scenario_summaries, seed_demo_tickets
from app.improvement import SupportImprovementService
from app.harvey import HarveyValueService
from app.models import Approval, ChangeDecision
from app.policy import PolicyEngine
from app.service import AutomationService
from app.tickets import MemoryTicketAdapter, ZammadAdapter

settings = get_settings()
project_root = Path(__file__).resolve().parent.parent
improvement = SupportImprovementService(
    project_root,
    settings.model_input_cost_per_million_aud,
    settings.model_output_cost_per_million_aud,
)
harvey = HarveyValueService()
memory = MemoryTicketAdapter()
seed_demo_tickets(memory)
tickets = ZammadAdapter(settings.zammad_url, settings.zammad_token or "") if settings.ticket_backend == "zammad" else memory
ai = (
    OpenAIDecisionProvider(
        settings.openai_api_key or "",
        settings.openai_model,
        settings.model_input_cost_per_million_aud,
        settings.model_output_cost_per_million_aud,
    )
    if settings.ai_provider == "openai"
    else FakeDecisionProvider()
)
ai.activate_prompt(improvement.active_version, improvement.prompt_text())
matters = MatterOpeningControlRoom()
service = AutomationService(
    tickets,
    matters,
    ai,
    PolicyEngine(),
    settings.experiment_spend_cap_aud,
    settings.experiment_model_call_cap,
)
app = FastAPI(
    title="Legal Technology Support Control Room",
    version="0.5.0",
    description="Synthetic ABL-style legal support desk and governed Harvey enablement demonstration.",
)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def branded_page(filename: str) -> HTMLResponse:
    html = (static_dir / filename).read_text(encoding="utf-8")
    html = html.replace("</head>", '<link rel="stylesheet" href="/static/brand.css"></head>')
    return HTMLResponse(html)


@app.get("/", include_in_schema=False)
def demo_home() -> HTMLResponse:
    return branded_page("overview.html")


@app.get("/workbench", include_in_schema=False)
def demo_workbench() -> HTMLResponse:
    return branded_page("workbench-menu.html")


@app.get("/workbench/full", include_in_schema=False)
def full_demo_workbench() -> HTMLResponse:
    return branded_page("index.html")


@app.get("/cheatsheet", include_in_schema=False)
def demo_cheatsheet() -> HTMLResponse:
    return branded_page("cheatsheet.html")


@app.get("/harvey-demo", include_in_schema=False)
def harvey_demo() -> HTMLResponse:
    return branded_page("harvey-demo.html")


@app.get("/proofs/{proof_name}", include_in_schema=False)
def proof_page(proof_name: str) -> HTMLResponse:
    pages = {
        "matter": "proof-matter.html",
        "support": "proof-support.html",
        "harvey": "proof-harvey.html",
        "improvement": "proof-improvement.html",
        "value": "proof-value.html",
    }
    filename = pages.get(proof_name)
    if not filename:
        raise HTTPException(404, "Proof point not found")
    return branded_page(filename)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "ai_provider": settings.ai_provider,
        "ticket_backend": settings.ticket_backend,
        "demo_boundary": "synthetic",
    }


@app.get("/demo/brief")
def demo_brief() -> dict:
    return DEMO_BRIEF


@app.get("/demo/scenarios")
def demo_scenarios() -> list[dict]:
    if not isinstance(tickets, MemoryTicketAdapter):
        raise HTTPException(400, "Synthetic scenarios are only available for the memory backend")
    return scenario_summaries()


@app.post("/demo/seed")
def seed() -> dict:
    if not isinstance(tickets, MemoryTicketAdapter):
        raise HTTPException(400, "Seed endpoint is only available for the memory backend")
    seed_demo_tickets(tickets)
    service.reset()
    improvement.reset()
    harvey.reset()
    ai.activate_prompt(improvement.active_version, improvement.prompt_text())
    return {
        "scenario_count": len(scenario_summaries()),
        "active_prompt_version": improvement.active_version,
        "harvey_runs": 0,
        "state": "reset",
    }


@app.get("/demo/scorecard")
def demo_scorecard() -> dict:
    return service.scorecard()


@app.get("/improvement/overview")
def improvement_overview() -> dict:
    return improvement.overview()


@app.get("/harvey/overview")
def harvey_overview() -> dict:
    return harvey.overview()


@app.post("/harvey/evaluate")
def evaluate_harvey() -> dict:
    return harvey.evaluate()


@app.post("/improvement/evaluate")
async def evaluate_improvement():
    try:
        return await improvement.evaluate()
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/improvement/decision")
def decide_improvement(decision: ChangeDecision):
    try:
        run = improvement.decide(decision)
        if decision.approved:
            ai.activate_prompt(improvement.active_version, improvement.prompt_text())
        return run
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/tickets/{ticket_id}/investigate")
async def investigate(ticket_id: str):
    try:
        return await service.investigate(ticket_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/tickets/{ticket_id}/case")
def get_case(ticket_id: str):
    if ticket_id not in service.cases:
        raise HTTPException(404, "Case not found")
    return service.cases[ticket_id]


@app.post("/tickets/{ticket_id}/approval")
async def approve(ticket_id: str, approval: Approval):
    try:
        return await service.approve(ticket_id, approval)
    except KeyError as exc:
        raise HTTPException(404, "Case not found") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc

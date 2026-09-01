from abc import ABC, abstractmethod
import httpx
from app.models import Ticket


class TicketAdapter(ABC):
    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> Ticket: ...

    @abstractmethod
    async def add_internal_note(self, ticket_id: str, body: str) -> None: ...

    @abstractmethod
    async def add_public_reply(self, ticket_id: str, body: str) -> None: ...


class MemoryTicketAdapter(TicketAdapter):
    def __init__(self) -> None:
        self.tickets: dict[str, Ticket] = {}
        self.notes: dict[str, list[str]] = {}
        self.replies: dict[str, list[str]] = {}

    def seed(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    async def get_ticket(self, ticket_id: str) -> Ticket:
        return self.tickets[ticket_id]

    async def add_internal_note(self, ticket_id: str, body: str) -> None:
        self.notes.setdefault(ticket_id, []).append(body)

    async def add_public_reply(self, ticket_id: str, body: str) -> None:
        self.replies.setdefault(ticket_id, []).append(body)


class ZammadAdapter(TicketAdapter):
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Token token={token}"}

    async def get_ticket(self, ticket_id: str) -> Ticket:
        async with httpx.AsyncClient(headers=self.headers) as client:
            ticket_response = await client.get(f"{self.base_url}/api/v1/tickets/{ticket_id}")
            ticket_response.raise_for_status()
            raw = ticket_response.json()
            articles_response = await client.get(f"{self.base_url}/api/v1/ticket_articles/by_ticket/{ticket_id}")
            articles_response.raise_for_status()
            articles = articles_response.json()
        first = articles[0] if articles else {}
        return Ticket(
            id=str(raw["id"]),
            subject=raw["title"],
            body=first.get("body", ""),
            requester=first.get("from", "unknown@example.test"),
            requester_role="Legal professional",
            category="general_it",
            status=str(raw.get("state_id", "open")),
        )

    async def _article(self, ticket_id: str, body: str, internal: bool) -> None:
        payload = {"ticket_id": int(ticket_id), "body": body, "content_type": "text/plain", "type": "note", "internal": internal}
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.post(f"{self.base_url}/api/v1/ticket_articles", json=payload)
            response.raise_for_status()

    async def add_internal_note(self, ticket_id: str, body: str) -> None:
        await self._article(ticket_id, body, True)

    async def add_public_reply(self, ticket_id: str, body: str) -> None:
        await self._article(ticket_id, body, False)

from abc import ABC, abstractmethod
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

from __future__ import annotations

from dataclasses import dataclass, field

from src.shared.domain.domain_event import DomainEvent
from src.shared.domain.entity import Entity


@dataclass(eq=False)
class AggregateRoot(Entity):
    """Base class for aggregate roots.

    Manages a list of uncommitted domain events that are collected during
    business operations and dispatched after persistence.
    """

    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def record_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Return and clear all pending domain events."""
        events = list(self._events)
        self._events.clear()
        return events

"""In-process domain event bus.

Services emit typed events via `event_bus.publish(event)`.
Listeners register with `@event_bus.subscribe(EventClass)`.

This decouples services from each other: the contract service does not need
to know that the notification service wants to react to ContractSigned.

For multi-process deployments, replace `_dispatch` with a Redis Streams or
RabbitMQ publisher; the subscriber interface stays unchanged.

Example:

    from events.event_bus import event_bus
    from events.domain_events import ContractSigned

    @event_bus.subscribe(ContractSigned)
    def on_contract_signed(event: ContractSigned) -> None:
        ...

    # In signing_service.py:
    event_bus.publish(ContractSigned(
        contract_id=..., version_id=..., user_id=..., signed_at=...
    ))
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class EventBus:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        # event_class -> list of handler callables
        self._subscribers: Dict[type, List[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_class: Type[T]) -> Callable:
        """Decorator — register a handler for *event_class*."""
        def decorator(fn: Callable[[T], None]) -> Callable[[T], None]:
            with self._lock:
                self._subscribers[event_class].append(fn)
            return fn
        return decorator

    def publish(self, event: Any) -> None:
        """Dispatch *event* to all registered subscribers synchronously.

        Each subscriber runs in the calling thread.  Exceptions in individual
        subscribers are logged and swallowed so one bad listener cannot break
        the publishing code.
        """
        handlers = []
        with self._lock:
            for cls in type(event).__mro__:
                handlers.extend(self._subscribers.get(cls, []))

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Event handler %r raised an exception for event %r",
                    handler,
                    event,
                )


# Module-level singleton used throughout the application
event_bus = EventBus()

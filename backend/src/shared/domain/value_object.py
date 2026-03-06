from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base class for all value objects.

    Value objects are immutable and equality is based on their attributes.
    """

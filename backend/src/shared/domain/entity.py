from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(eq=False)
class Entity:
    """Base class for all domain entities.

    Identity is based solely on the entity's id, not attribute values.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4, kw_only=True)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

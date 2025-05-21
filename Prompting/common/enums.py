from enum import Enum

class AgendaStatus(str, Enum):
    PENDING = "pending",
    SKIPPED = "skipped",
    COMPLETE = "complete"
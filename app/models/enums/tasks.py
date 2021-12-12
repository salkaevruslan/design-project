import enum


class TaskPriority(enum.Enum):
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    LOW = "LOW"


class TaskStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    DONE = "DONE"
    SUGGESTED = "SUGGESTED"


class TaskType(enum.Enum):
    UNDEFINED = "UNDEFINED"
    BUSINESS = "BUSINESS"
    DONE = "MEETING"
    NOTE = "NOTE"
    SUGGESTED = "OTHER"


class TaskOwnerType(enum.Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    GROUP_SUGGESTED = "GROUP_SUGGESTED"

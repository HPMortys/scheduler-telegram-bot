import enum

DB_FILE = "identifier.sqlite"


class NotificationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

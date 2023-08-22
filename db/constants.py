import enum
from utils_general.config_utils import get_environ_var_value

DB_FILE = get_environ_var_value("", default="D:\\IT_projects\\Scheduler\\identifier.sqlite")
# sqlite:///identifier.sqlite


class NotificationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

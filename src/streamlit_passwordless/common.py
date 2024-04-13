r"""Functions that are common to several modules."""

# Standard library
from datetime import datetime
import logging
from zoneinfo import ZoneInfo

# Third party

# Local


logger = logging.getLogger(__name__)


def get_current_datetime(tz='UTC') -> datetime:
    r"""Get the current datetime based on the timezone `tz`."""

    return datetime.now(tz=ZoneInfo(tz))

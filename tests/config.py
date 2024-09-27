r"""Configuration for the test suite."""

# Standard library
from typing import Any, TypeAlias
from zoneinfo import ZoneInfo

# Third party

# Local

TZ_UTC = ZoneInfo('UTC')
ModelData: TypeAlias = dict[str, Any]

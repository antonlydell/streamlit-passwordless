r"""Configuration for the test suite."""

# Standard library
from typing import Any, TypeAlias
from zoneinfo import ZoneInfo

# Local
from streamlit_passwordless.database import Session, SessionFactory
from streamlit_passwordless.database.models import CustomRole, Role

TZ_UTC = ZoneInfo('UTC')
ModelData: TypeAlias = dict[str, Any]
DbWithRoles: TypeAlias = tuple[Session, SessionFactory, tuple[Role, Role, Role, Role]]
DbWithCustomRoles: TypeAlias = tuple[Session, SessionFactory, tuple[CustomRole, CustomRole]]

r"""The schemas for the user model."""

# Standard library
import uuid
from datetime import datetime

# Third party
from pydantic import Field, field_validator

# Local
from .core import SchemaBaseModel


class UserBase(SchemaBaseModel):
    r"""The base schema of a user.

    Parameters
    ----------
    user_id : str or None, default None
        The unique ID of the user, which serves as the primary key in the database.
        If None it will be generated as a uuid.
    """

    user_id: str | None = Field(default=None, validate_default=True)

    @field_validator('user_id')
    def generate_user_id(cls, v: str | None) -> str:
        r"""Generate a user ID if not supplied."""

        return str(uuid.uuid4()) if v is None else v


class UserCreate(UserBase):
    r"""The schema for creating a new user.

    Parameters
    ----------
    username : str
        The username of the user.

    ad_username : str or None, default None
        The active directory username of the user.

    displayname : str or None, default None
        A descriptive name of the user that is easy to understand for a human.

    disabled : bool, default False
        If False the user is enabled and if True the user is disabled.
        A disabled user is not able to register credentials or sign in.

    disabled_timestamp : datetime or None, default None
        The timestamp when the user was disabled.
    """

    username: str
    ad_username: str | None = None
    displayname: str | None = None
    disabled: bool = False
    disabled_timestamp: datetime | None = None

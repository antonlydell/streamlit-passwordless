r"""The data models of streamlit-passwordless."""

# Standard library
import uuid
from datetime import datetime

# Third party
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, ValidationError, field_validator

# Local
from . import exceptions


class BaseModel(PydanticBaseModel):
    r"""The BaseModel that all models inherit from."""

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            raise exceptions.StreamlitPasswordlessError(str(e)) from None


class Email(BaseModel):
    r"""An Email address of a user.

    Parameters
    ----------
    email_id : int or None, default None
        The unique identifier of the email and the primary key in the database.
        None is used when the email is not persisted in the database.

    user_id : str
        The unique ID of the user the email address belongs to.

    email : str
        An email address of a user. Must be unique across all users.

    is_primary : bool
        True if the email address is the primary email address of the user
        and False otherwise. A user can only have one primary email address.

    verified_at : datetime or None, default None
        The timestamp in UTC when the email address was verified by the user.

    disabled : bool, default False
        If the email address is disabled or not.

    disabled_timestamp : datetime or None, default None
        The timestamp in UTC when the email address was disabled.
    """

    email_id: int | None = None
    user_id: str
    email: str
    is_primary: bool
    verified_at: datetime | None = None
    disabled: bool = False
    disabled_timestamp: datetime | None = None


class User(BaseModel):
    r"""A user within the streamlit-passwordless data model.

    Parameters
    ----------
    username : str
        The username of the user.

    user_id : str | None, default None
        The unique ID of the user which serves as the primary key in the database.
        If None it will be generated as a uuid.

    email : str | None, default None
        The email address of the user.

    displayname : str | None, default None
        A descriptive name of the user that is easy to understand for a human.

    aliases : tuple[str, ...] | str | None, default None
        Additional ID:s that can be used to identify the user when signing in.
        A string with aliases separated by semicolon ";" can be used to supply multiple
        aliases if tuple is not used.
    """

    username: str
    user_id: str | None = Field(default=None, validate_default=True)
    email: str | None = None
    displayname: str | None = None
    aliases: tuple[str, ...] | str | None = Field(default=None, validate_default=True)

    def __hash__(self) -> int:
        return hash(self.user_id)

    @field_validator('user_id')
    def generate_user_id(cls, v: str | None) -> str:
        r"""Generate a user ID if not supplied."""

        return str(uuid.uuid4()) if v is None else v

    @field_validator('aliases')
    def process_aliases(cls, aliases: tuple[str, ...] | str | None) -> tuple[str, ...] | None:
        r"""Convert multiple aliases in a string to a tuple by splitting on the semicolon ";"."""

        if isinstance(aliases, str):
            return tuple(v for a in aliases.split(';') if (v := a.strip()))
        else:
            return aliases

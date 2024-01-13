r"""The data models of streamlit-passwordless."""

# Standard library
import uuid

# Third party
from pydantic import BaseModel as PydanticBaseModel, validator, ValidationError

# Local
from . import exceptions


class BaseModel(PydanticBaseModel):
    r"""The BaseModel that all models inherit from."""

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            raise exceptions.StreamlitPasswordlessError(str(e)) from None


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
    user_id: str | None = None
    email: str | None = None
    displayname: str | None = None
    aliases: tuple[str, ...] | str | None = None

    @validator('user_id', always=True)
    def generate_user_id(cls, v: str | None, values) -> str:
        r"""Generate a user ID if not supplied."""

        return str(uuid.uuid4()) if v is None else v

    @validator('aliases', always=True)
    def process_aliases(cls, aliases: tuple[str, ...] | str | None) -> tuple[str, ...] | None:
        r"""Convert multiple aliases in a string to a tuple by splitting on the semicolon ";"."""

        if isinstance(aliases, str):
            return tuple(v for a in aliases.split(';') if (v := a.strip()))
        else:
            return aliases

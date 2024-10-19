r"""The data models of streamlit-passwordless."""

# Standard library
import uuid
from datetime import datetime
from enum import StrEnum

# Third party
from pydantic import AliasChoices
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, ValidationError, field_validator

# Local
from . import exceptions


class UserRoleName(StrEnum):
    r"""The predefined user role names of streamlit-passwordless.

    These roles are created in the database when the database is initialized.
    The default role of a new user is :attr:`UserRoleName.USER`.

    Members
    -------
    VIEWER
        A user that can only view data within an application.

    USER
        The standard user with normal privileges. When a user is created it is
        assigned this role by default.

    SUPERUSER
        A user with higher privileges that can perform certain
        operations that a normal `USER` can not.

    ADMIN
        An admin has full access to everything. Only admin users may sign in to the admin page
        and manage the users of the application. An application should have at least one admin.
    """

    VIEWER = 'Viewer'
    USER = 'User'
    SUPERUSER = 'SuperUser'
    ADMIN = 'Admin'


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


class UserSignIn(BaseModel):
    r"""A model of a user sign in with a passkey credential.

    Parameters
    ----------
    user_sign_in_id : int or None, default None
        The unique ID of sign in entry. The primary key of the database table.
        None is used when the sign in entry is not persisted in the database.

    user_id : str
        The unique ID of the user that signed in to the application.

    sign_in_timestamp : datetime
        The timestamp in timezone UTC when the user signed in. Alias `timestamp`.

    success : bool
        True if the user was successfully signed in and False otherwise.

    origin : str
        The domain name or IP-address of the application the user signed in to.

    device : str
        The device the user signed in from. E.g. a web browser.

    country : str
        The country code of the country that the user signed in from. E.g. SE for Sweden.

    credential_nickname : str
        The nickname of the passkey that was used to sign in. Alias `nickname`.

    credential_id : str
        The ID of the passkey credential used to sign in.

    sign_in_type : str
        The type of sign in method. E.g. 'passkey_signin'. Alias `type`.

    rp_id : str or None
        The ID of the relaying party, which is the server that
        verifies the credentials during the sign in process.
    """

    user_sign_in_id: int | None = None
    user_id: str
    sign_in_timestamp: datetime = Field(
        validation_alias=AliasChoices('sign_in_timestamp', 'timestamp')
    )
    success: bool
    origin: str
    device: str
    country: str
    credential_nickname: str = Field(
        validation_alias=AliasChoices('credential_nickname', 'nickname')
    )
    credential_id: str
    sign_in_type: str = Field(validation_alias=AliasChoices('sign_in_type', 'type'))
    rp_id: str | None = None


class User(BaseModel):
    r"""A user within the streamlit-passwordless data model.

    Parameters
    ----------
    user_id : str or None, default None
        The unique ID of the user which serves as the primary key in the database.
        If None it will be generated as a uuid.

    username : str
        The username of the user. It must be unique across all users.

    ad_username : str or None, default None
        The active directory username of the user if such exists.

    displayname : str or None, default None
        A descriptive name of the user that is easy to understand for a human.

    verified_at : datetime or None, default None
        The timestamp in UTC when the user was verified. A user is verified when
        at least one verified email address is associated with the user.

    disabled : bool, default False
        If False the user is enabled and if True the user is disabled.
        A disabled user is not able to register credentials or sign in.

    disabled_timestamp : datetime or None, default None
        The timestamp in UTC when the user was disabled.

    emails : list[Email] or None, default None
        The email addresses associated with the user.

    sign_in : UserSignIn or None, default None
        Info about when the user signed in to the application.

    aliases : tuple[str, ...] or str or None, default None
        Additional ID:s that can be used to identify the user when signing in.
        A string with aliases separated by semicolon ";" can be used to supply multiple
        aliases if tuple is not used.
    """

    user_id: str | None = Field(default=None, validate_default=True)
    username: str
    ad_username: str | None = None
    displayname: str | None = None
    verified_at: datetime | None = None
    disabled: bool = False
    disabled_timestamp: datetime | None = None
    emails: list[Email] | None = None
    sign_in: UserSignIn | None = None
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

    @property
    def is_authenticated(self) -> bool:
        r"""Check if the user is authenticated with the application."""

        if (sign_in := self.sign_in) is None:
            return False
        else:
            return sign_in.user_id == self.user_id and sign_in.success

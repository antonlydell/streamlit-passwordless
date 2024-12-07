r"""The data models of streamlit-passwordless."""

# Standard library
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Self

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


class BaseRole(BaseModel):
    r"""The base model for the models :class:`Role` and :class:`CustomRole`.

    :class:`BaseRole` should be subclassed and not used on its own.
    """

    model_config = ConfigDict(frozen=True)

    role_id: int | None = None
    name: str
    rank: int
    description: str | None = None


class Role(BaseRole):
    r"""The role of a user.

    A :class:`User` is associated with a role to manage its privileges within an application.

    Parameters
    ----------
    role_id : int or None, default None
        The unique identifier of the role and the primary key in the database.
        If None the role is not persisted in the database.

    name : str
        The name of the role. Must be unique.

    rank : int
        The rank of the role. A role with a higher rank has more privileges. Used
        for comparing roles against one another. Two roles may have the same rank.

    description : str or None, default None
        A description of the role.
    """

    @classmethod
    def create_viewer(cls) -> Self:
        r"""Create the VIEWER role."""

        return cls(
            name=UserRoleName.VIEWER,
            rank=1,
            description='A user that can only view data within an application.',
        )

    @classmethod
    def create_user(cls) -> Self:
        r"""Create the USER role, which is the default for a new user."""

        return cls(
            name=UserRoleName.USER,
            rank=2,
            description=(
                'The standard user with normal privileges. The default role for a new user.'
            ),
        )

    @classmethod
    def create_superuser(cls) -> Self:
        r"""Create the SUPERUSER role."""

        return cls(
            name=UserRoleName.SUPERUSER,
            rank=3,
            description=(
                'A user with higher privileges that can perform certain '
                'operations that a normal `USER` can not.'
            ),
        )

    @classmethod
    def create_admin(cls) -> Self:
        r"""Create the ADMIN role."""

        return cls(
            name=UserRoleName.ADMIN,
            rank=4,
            description=(
                'An admin has full access to everything. Only admin users may sign '
                'in to the admin page and manage the users of the application. '
                'An application should have at least one admin.'
            ),
        )


class CustomRole(BaseRole):
    r"""A custom role for a user.

    A :class:`User` may have none or multiple custom roles
    that are defined specifically for each application.

    Parameters
    ----------
    role_id : int or None, default None
        The unique identifier of the role and the primary key in the database.
        If None the role is not persisted in the database.

    name : str
        The name of the role. Must be unique.

    rank : int
        The rank of the role. A role with a higher rank has more privileges. Used
        for comparing roles against one another. Two roles may have the same rank.

    description : str or None, default None
        A description of the role.
    """


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

    rank : int
        The rank of the email, where 1 defines the primary email, 2 the secondary
        and 3 the tertiary etc ... A user can only have one email of each rank.

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
    rank: int
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

    role : Role, default `Role(name=UserRoleName.USER)`
        The role of the user. If not specified the default
        :attr:`UserRoleName.USER` role is assigned.

    custom_roles : dict[str, CustomRole] or None, default None
        The custom roles of the user. The role name is mapped to the :class:`CustomRole` model.
        A user may have none or many custom roles.

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
    role: Role = Field(default_factory=Role.create_user)
    custom_roles: dict[str, CustomRole] | None = None
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

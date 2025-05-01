r"""The models that represent tables in the database."""

# Standard library
import os
from datetime import datetime
from enum import StrEnum
from typing import ClassVar, Optional, Self

# Third party
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Index, MetaData, Table, UniqueConstraint, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    attribute_keyed_dict,
    mapped_column,
    relationship,
)

SCHEMA: str | None = os.getenv('STP_DB_SCHEMA')
metadata_obj = MetaData(schema=SCHEMA)

modified_at_column: Mapped[Optional[datetime]] = mapped_column(
    TIMESTAMP(), onupdate=func.current_timestamp()
)
created_at_column: Mapped[datetime] = mapped_column(
    TIMESTAMP(), server_default=func.current_timestamp()
)


def _column_to_str(col: object) -> str:
    r"""Convert a column value to string format.

    To be used for the `__repr__` methods of the models.
    """

    return col.isoformat() if isinstance(col, datetime) else repr(col)


class Base(DeclarativeBase):
    r"""The base model all database models will inherit from.

    It defines the schema/user where the tables will be created in the
    database and the columns, which are common for all tables.

    Class variables
    ---------------
    columns__repr__ : ClassVar[tuple[str, ...]], default tuple()
        The names of the columns that should be part of the `__repr__` method output.
        Each model should define this variable. If columns are defined on :class:`Base`
        they should not be part of `columns__repr__`.

    indent_space__repr__ : ClassVar[str], default ' ' * 4
        The indentation space used for each column in the `__repr__` method.
    """

    columns__repr__: ClassVar[tuple[str, ...]] = tuple()
    indent_space__repr__: ClassVar[str] = ' ' * 4

    metadata = metadata_obj

    def __repr__(self) -> str:
        r"""A string representation of the model."""

        indent = self.indent_space__repr__
        output = f'{self.__class__.__name__}(\n'

        for col in self.columns__repr__:
            value = getattr(self, col)
            value = _column_to_str(value)
            output += f'{indent}{col}={value},\n'

        output += ')'

        return output


class ModifiedAndCreatedColumnMixin:
    r"""Add columns for when a record was last modified and created in a table.

    Parameters
    ----------
    modified_at : datetime or None
        The timestamp at which the record was last modified (UTC).

    modified_by : str or None
        The ID of the user that last modified the record.

    created_at : datetime
        The timestamp at which the record was created (UTC).
        Defaults to current timestamp.

    created_by : str or None
        The ID of the user that created the record.

    A table model should inherit from this class prior to :class:`Base`.
    E.g. creating the user model:

    .. code-block:: python

        class User(ModifiedAndCreatedColumnMixin, Base):
            pass
    """

    modified_at: Mapped[Optional[datetime]] = modified_at_column
    modified_by: Mapped[Optional[str]]
    created_at: Mapped[datetime] = created_at_column
    created_by: Mapped[Optional[str]]


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


class Role(ModifiedAndCreatedColumnMixin, Base):
    r"""The role of a user.

    A :class:`User` is associated with a role to manage its privileges within an application.
    The available roles are predefined by streamlit-passwordless, but can be extended if needed.

    Parameters
    ----------
    role_id : int
        The primary key of the table.

    name : str
        The name of the role. Must be unique.

    rank : int
        The rank of the role. A role with a higher rank has more privileges. Used
        for comparing roles against one another. Two roles may have the same rank.

    description : str or None, default None
        A description of the role.

    modified_at : datetime or None
        The timestamp at which the role was last modified (UTC).

    modified_by : str or None
        The ID of the user that last modified the role.

    created_at : datetime
        The timestamp at which the role was created (UTC).
        Defaults to current timestamp.

    created_by : str or None
        The ID of the user that created the role.

    users : list[User]
        The users that have the role assigned.
    """

    columns__repr__: ClassVar[tuple[str, ...]] = (
        'role_id',
        'name',
        'rank',
        'description',
        'modified_at',
        'modified_by',
        'created_at',
        'created_by',
    )

    __tablename__ = 'stp_role'

    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    rank: Mapped[int]
    description: Mapped[str | None]
    users: Mapped[list['User']] = relationship(back_populates='role')

    @classmethod
    def create_viewer(cls) -> Self:
        r"""Create the VIEWER role."""

        return cls(
            role_id=1,
            name=UserRoleName.VIEWER,
            rank=1,
            description='A user that can only view data within an application.',
        )

    @classmethod
    def create_user(cls) -> Self:
        r"""Create the USER role, which is the default for a new user."""

        return cls(
            role_id=2,
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
            role_id=3,
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
            role_id=4,
            name=UserRoleName.ADMIN,
            rank=4,
            description=(
                'An admin has full access to everything. Only admin users may sign '
                'in to the admin page and manage the users of the application. '
                'An application should have at least one admin.'
            ),
        )


Index(f'{Role.__tablename__}_name_ix', Role.name)


class CustomRole(ModifiedAndCreatedColumnMixin, Base):
    r"""The custom roles of a user.

    Custom roles can be defined specifically for each application.
    A user may have none or multiple custom roles, which may grant
    application specific privileges or hide/expose specific pages.

    Parameters
    ----------
    role_id : int
        The primary key of the table.

    name : str
        The name of the role.

    rank : int
        The rank of the role. A role with a higher rank has more privileges. Used
        for comparing roles against one another. Two roles may have the same rank.

    description : str or None, default None
        A description of the role.

    modified_at : datetime or None
        The timestamp at which the custom role was last modified (UTC).

    modified_by : str or None
        The ID of the user that last modified the custom role.

    created_at : datetime
        The timestamp at which the custom role was created (UTC).
        Defaults to current timestamp.

    created_by : str or None
        The ID of the user that created the custom role.

    users : dict[str, User]
        A mapping of the users that have the custom role assigned.
        The key is the username of the user.
    """

    columns__repr__: ClassVar[tuple[str, ...]] = (
        'role_id',
        'name',
        'rank',
        'description',
        'modified_at',
        'modified_by',
        'created_at',
        'created_by',
    )

    __tablename__ = 'stp_custom_role'

    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    rank: Mapped[int]
    description: Mapped[Optional[str]]
    users: Mapped[dict[str, 'User']] = relationship(
        secondary='stp_user_custom_role_link',
        back_populates='custom_roles',
        collection_class=attribute_keyed_dict('username'),
    )


Index(f'{CustomRole.__tablename__}_name_ix', CustomRole.name)

# Association table for the many-to-many relationship between User and CustomRole.
user_custom_role_link = Table(
    'stp_user_custom_role_link',
    Base.metadata,
    Column('user_id', ForeignKey('stp_user.user_id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', ForeignKey('stp_custom_role.role_id'), primary_key=True),
)


class User(ModifiedAndCreatedColumnMixin, Base):
    r"""The user table.

    Parameters
    ----------
    user_id : str
        The unique ID of the user. The primary key of the table.

    username : str
        The username of the user. It must be unique across all users.

    ad_username : Optional[str]
        The active directory username of the user.

    displayname : Optional[str]
        A descriptive name of the user that is easy to understand for a human.

    role_id : int
        The unique id of the role associated with the user.

    verified : bool, default False
        True if a user is verified and False otherwise. A user is verified when
        at least one verified email address is associated with the user.

    verified_at : Optional[datetime]
        The timestamp in UTC when the user was verified.

    disabled : bool, default False
        If False the user is enabled and if True the user is disabled.
        A disabled user is not able to register credentials or sign in.

    disabled_at : Optional[datetime]
        The timestamp in UTC when the user was disabled.

    modified_at : datetime or None
        The timestamp at which the user was last modified (UTC).

    modified_by : str or None
        The ID of the user that last modified the user.

    created_at : datetime
        The timestamp at which the user was created (UTC).
        Defaults to current timestamp.

    created_by : str or None
        The ID of the user that created the user.

    role : Role
        The role of the user.

    custom_roles : dict[str, CustomRole]
        The custom roles of the user. The role name is mapped to the :class:`CustomRole` model.

    emails : list[Email]
        The email addresses associated with the user.

    sign_ins : list[UserSignIn]
        Info about when the user has signed in to the application.
    """

    columns__repr__: ClassVar[tuple[str, ...]] = (
        'user_id',
        'username',
        'ad_username',
        'displayname',
        'role_id',
        'verified',
        'verified_at',
        'disabled',
        'disabled_at',
        'modified_at',
        'modified_by',
        'created_at',
        'created_by',
    )

    __tablename__ = 'stp_user'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    ad_username: Mapped[Optional[str]]
    displayname: Mapped[Optional[str]]
    role_id: Mapped[int] = mapped_column(ForeignKey(Role.role_id))
    verified: Mapped[bool] = mapped_column(default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    disabled: Mapped[bool] = mapped_column(default=False)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    role: Mapped[Role] = relationship(back_populates='users')
    custom_roles: Mapped[dict[str, CustomRole]] = relationship(
        secondary='stp_user_custom_role_link',
        collection_class=attribute_keyed_dict('name'),
        back_populates='users',
        passive_deletes=True,
    )
    emails: Mapped[list['Email']] = relationship(
        back_populates='user', cascade='delete, delete-orphan', order_by='Email.rank'
    )
    sign_ins: Mapped[list['UserSignIn']] = relationship(
        back_populates='user', cascade='delete, delete-orphan'
    )


Index(f'{User.__tablename__}_username_ix', User.username)
Index(f'{User.__tablename__}_ad_username_ix', User.ad_username)
Index(f'{User.__tablename__}_disabled_ix', User.disabled)


class Email(ModifiedAndCreatedColumnMixin, Base):
    r"""Email addresses of a user.

    Parameters
    ----------
    email_id : int
        The primary key of the table.

    user_id : str
        The unique ID of the user the email address belongs to.

    email : str
        An email address of a user. Must be unique.

    rank : int
        The rank of the email, where 1 defines the primary email, 2 the secondary
        and 3 the tertiary etc ... A user can only have one email of each rank.

    verified_at : Optional[datetime]
        The timestamp in UTC when the email address was verified by the user.

    disabled : bool, default False
        If the email address is disabled or not.

    disabled_timestamp : Optional[datetime]
        The timestamp in UTC when the email address was disabled.

    modified_at : datetime or None
        The timestamp at which the email was last modified (UTC).

    modified_by : str or None
        The ID of the user that last modified the email.

    created_at : datetime
        The timestamp at which the email was created (UTC).
        Defaults to current timestamp.

    created_by : str or None
        The ID of the user that created the email.

    user : User
        The user object the email address belongs to.
    """

    columns__repr__: ClassVar[tuple[str, ...]] = (
        'email_id',
        'user_id',
        'email',
        'rank',
        'verified_at',
        'disabled',
        'disabled_timestamp',
        'modified_at',
        'modified_by',
        'created_at',
        'created_by',
    )

    __tablename__ = 'stp_email'
    __table_args__ = (UniqueConstraint('user_id', 'rank', name=f'{__tablename__}_user_id_rank_iu'),)

    email_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.user_id, ondelete='CASCADE'))
    email: Mapped[str] = mapped_column(unique=True)
    rank: Mapped[int]
    verified_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    disabled: Mapped[bool] = mapped_column(default=False)
    disabled_timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    user: Mapped['User'] = relationship(back_populates='emails')


Index(f'{Email.__tablename__}_email_ix', Email.email)
Index(f'{Email.__tablename__}_user_id_ix', Email.user_id)


class UserSignIn(Base):
    r"""A logging table of when a user has signed in to the application.

    Parameters
    ----------
    user_sign_in_id : int
        The primary key of the table.

    user_id : str
        The unique ID of the user that signed in to the application.

    sign_in_timestamp : datetime
        The timestamp in timezone UTC when the user signed in.

    success : bool
        True if the user was successfully signed in and False otherwise.

    origin : str
        The domain name or IP-address of the application the user signed in to.

    device : str
        The device the user signed in from. E.g. a web browser.

    country : str
        The country code of the country that the user signed in from. E.g. SE for Sweden.

    credential_nickname : str
        The nickname of the passkey that was used to sign in.

    credential_id : str
        The ID of the passkey credential used to sign in.

    sign_in_type : str
        The type of sign in method. E.g. 'passkey_signin'.

    rp_id : str or None
        The ID of the relaying party, which is the server that
        verifies the credentials during the sign in process.

    created_at : datetime
        The timestamp at which the user sign in record was created (UTC).
        Defaults to current timestamp.

    user : User
        The user object the sign in entry belongs to.
    """

    columns__repr__: ClassVar[tuple[str, ...]] = (
        'user_sign_in_id',
        'user_id',
        'sign_in_timestamp',
        'success',
        'origin',
        'device',
        'country',
        'credential_nickname',
        'credential_id',
        'sign_in_type',
        'rp_id',
        'created_at',
    )

    __tablename__ = 'stp_user_sign_in'

    user_sign_in_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.user_id, ondelete='CASCADE'))
    sign_in_timestamp: Mapped[datetime] = mapped_column(TIMESTAMP())
    success: Mapped[bool]
    origin: Mapped[str]
    device: Mapped[str]
    country: Mapped[str]
    credential_nickname: Mapped[str]
    credential_id: Mapped[str]
    sign_in_type: Mapped[str]
    rp_id: Mapped[Optional[str]]
    created_at: Mapped[datetime] = created_at_column
    user: Mapped['User'] = relationship(back_populates='sign_ins')


Index(f'{UserSignIn.__tablename__}_ix1', UserSignIn.user_id, UserSignIn.sign_in_timestamp)
Index(f'{UserSignIn.__tablename__}_ix2', UserSignIn.origin)

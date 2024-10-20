r"""The models that represent tables in the database."""

# Standard library
from datetime import datetime
from typing import ClassVar, Optional

# Third party
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Index, Table, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    attribute_keyed_dict,
    mapped_column,
    relationship,
)

# Local

SCHEMA: str | None = None


def _timestamp_col_to_str(col: datetime | None) -> str | None:
    r"""Convert an optional datetime column to an iso-formatted string.

    To be used for the `__repr__` methods of the models.
    """

    return col if col is None else col.isoformat()


class Base(DeclarativeBase):
    r"""The base model all database models will inherit from.

    It defines the schema/user where the tables will be created in the
    database and the columns, which are common for all tables.

    Class variables
    ---------------
    _columns__repr__: ClassVar[tuple[str, ...]], default tuple()
        The names of the columns that should be part of the `__repr__` method output.
        Each model should define this variable. The columns defined on `Base` should
        not be part of `_columns__repr__`.

    _indent_space__repr__ : ClassVar[str], default ' ' * 4
        The indentation space used for each column in the `__repr__` method.

    Parameters
    ----------
    modified_at : datetime
        The timestamp at which the table record was latest modified (UTC).

    created_at : datetime
        The timestamp at which the table record was created (UTC).
    """

    _columns__repr__: ClassVar[tuple[str, ...]] = tuple()
    _indent_space__repr__: ClassVar[str] = ' ' * 4

    __table_args__ = {'schema': SCHEMA}

    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), server_default=func.current_timestamp()
    )

    @property
    def _modified_at_created_at_as_str(self) -> str:
        r"""Stringify the timestamp columns modified_at and created_at.

        To be used in the `__repr__` methods of the models.
        """

        indent = self._indent_space__repr__
        return (
            f'{indent}modified_at={_timestamp_col_to_str(self.modified_at)},\n'
            f'{indent}created_at={_timestamp_col_to_str(self.created_at)},'
        )

    def __repr__(self) -> str:
        r"""A string representation of the model."""

        indent = self._indent_space__repr__
        output = f'{self.__class__.__name__}(\n'

        for col in self._columns__repr__:
            value = getattr(self, col)
            value = _timestamp_col_to_str(value) if isinstance(value, datetime) else repr(value)
            output += f'{indent}{col}={value},\n'

        output += f'{self._modified_at_created_at_as_str}\n)'

        return output


class Role(Base):
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

    users : list[User]
        The users that have the role assigned.
    """

    _columns__repr__: ClassVar[tuple[str, ...]] = ('role_id', 'name', 'rank', 'description')

    __tablename__ = 'stp_role'

    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    rank: Mapped[int]
    description: Mapped[str | None]
    users: Mapped[list['User']] = relationship(back_populates='role')


Index(f'{Role.__tablename__}_name_ix', Role.name)


class CustomRole(Base):
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

    users : dict[str, User]
        A mapping of the users that have the custom role assigned.
        The key is the username of the user.
    """

    _columns__repr__: ClassVar[tuple[str, ...]] = ('role_id', 'name', 'rank', 'description')

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
    Column('user_id', ForeignKey('stp_user.user_id', ondelete='CASCADE')),
    Column('role_id', ForeignKey('stp_custom_role.role_id')),
)


class User(Base):
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

    verified_at : Optional[datetime]
        The timestamp in UTC when the user was verified. A user is verified, when
        at least one verified email address is associated with the user.

    disabled : bool, default False
        If False the user is enabled and if True the user is disabled.
        A disabled user is not able to register credentials or sign in.

    disabled_timestamp : Optional[datetime]
        The timestamp in UTC when the user was disabled.

    role : Role
        The role of the user.

    custom_roles : dict[str, CustomRole]
        The custom roles of the user. The role name is mapped to the :class:`CustomRole` model.

    emails : list[Email]
        The email addresses associated with the user.

    sign_ins : list[UserSignIn]
        Info about when the user has signed in to the application.
    """

    _columns__repr__: ClassVar[tuple[str, ...]] = (
        'user_id',
        'username',
        'ad_username',
        'displayname',
        'role_id',
        'verified_at',
        'disabled',
        'disabled_timestamp',
    )

    __tablename__ = 'stp_user'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    ad_username: Mapped[Optional[str]]
    displayname: Mapped[Optional[str]]
    role_id: Mapped[int] = mapped_column(ForeignKey(Role.role_id))
    verified_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    disabled: Mapped[bool] = mapped_column(default=False)
    disabled_timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    role: Mapped[Role] = relationship(back_populates='users')
    custom_roles: Mapped[dict[str, CustomRole] | None] = relationship(
        secondary='stp_user_custom_role_link',
        collection_class=attribute_keyed_dict('name'),
        back_populates='users',
        passive_deletes=True,
    )
    emails: Mapped[list['Email']] = relationship(
        back_populates='user', cascade='delete, delete-orphan'
    )
    sign_ins: Mapped[list['UserSignIn']] = relationship(back_populates='user')


Index(f'{User.__tablename__}_username_ix', User.username)
Index(f'{User.__tablename__}_ad_username_ix', User.ad_username)
Index(f'{User.__tablename__}_disabled_ix', User.disabled)


class Email(Base):
    r"""Email addresses of a user.

    Parameters
    ----------
    email_id : int
        The primary key of the table.

    user_id : str
        The unique ID of the user the email address belongs to.

    email : str
        An email address of a user. Must be unique.

    is_primary : bool
        True if the email address is the primary email address of the user
        and False otherwise. A user can only have one primary email address.

    verified_at : Optional[datetime]
        The timestamp in UTC when the email address was verified by the user.

    disabled : bool, default False
        If the email address is disabled or not.

    disabled_timestamp : Optional[datetime]
        The timestamp in UTC when the email address was disabled.

    user : User
        The user object the email address belongs to.
    """

    _columns__repr__: ClassVar[tuple[str, ...]] = (
        'email_id',
        'user_id',
        'email',
        'is_primary',
        'verified_at',
        'disabled',
        'disabled_timestamp',
    )

    __tablename__ = 'stp_email'

    email_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.user_id, ondelete='CASCADE'))
    email: Mapped[str] = mapped_column(unique=True)
    is_primary: Mapped[bool]
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

    user : User
        The user object the sign in entry belongs to.
    """

    _columns__repr__: ClassVar[tuple[str, ...]] = (
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
    )

    __tablename__ = 'stp_user_sign_in'

    user_sign_in_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.user_id))
    sign_in_timestamp: Mapped[datetime] = mapped_column(TIMESTAMP())
    success: Mapped[bool]
    origin: Mapped[str]
    device: Mapped[str]
    country: Mapped[str]
    credential_nickname: Mapped[str]
    credential_id: Mapped[str]
    sign_in_type: Mapped[str]
    rp_id: Mapped[Optional[str]]
    user: Mapped['User'] = relationship(back_populates='sign_ins')


Index(f'{UserSignIn.__tablename__}_ix1', UserSignIn.user_id, UserSignIn.sign_in_timestamp)
Index(f'{UserSignIn.__tablename__}_ix2', UserSignIn.origin)

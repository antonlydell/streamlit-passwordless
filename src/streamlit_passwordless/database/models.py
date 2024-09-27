r"""The models that represent tables in the database."""

# Standard library
from datetime import datetime
from typing import Optional

# Third party
from sqlalchemy import TIMESTAMP, ForeignKey, Index, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Local

SCHEMA: str | None = None


class Base(DeclarativeBase):
    r"""The base model all database models will inherit from.

    It defines the schema/user where the tables will be created in the
    database and the columns, which are common for all tables.

    Parameters
    ----------
    modified_at : datetime
        The timestamp at which the table record was latest modified (UTC).

    created_at : datetime
        The timestamp at which the table record was created (UTC).
    """

    __table_args__ = {'schema': SCHEMA}

    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), server_default=func.current_timestamp()
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

    verified_at : Optional[datetime]
        The timestamp in UTC when the user was verified. A user is verified, when
        at least one verified email address is associated with the user.

    disabled : bool, default False
        If False the user is enabled and if True the user is disabled.
        A disabled user is not able to register credentials or sign in.

    disabled_timestamp : Optional[datetime]
        The timestamp in UTC when the user was disabled.

    emails : list[Email]
        The email addresses associated with the user.

    sign_ins : list[UserSignIn]
        Info about when the user has signed in to the application.
    """

    __tablename__ = 'stp_user'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    ad_username: Mapped[Optional[str]]
    displayname: Mapped[Optional[str]]
    verified_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    disabled: Mapped[bool] = mapped_column(default=False)
    disabled_timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    emails: Mapped[list['Email']] = relationship(back_populates='user')
    sign_ins: Mapped[list['UserSignIn']] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(\n'
            f'    user_id={self.user_id},\n'
            f'    username={self.username},\n'
            f'    ad_username={self.username},\n'
            f'    displayname={self.displayname},\n'
            f'    verified_at={self.verified_at},\n'
            f'    disabled={self.disabled},\n'
            f'    disabled_timestamp={self.disabled_timestamp},\n)'
        )


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

    __tablename__ = 'stp_email'

    email_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.user_id))
    email: Mapped[str] = mapped_column(unique=True)
    is_primary: Mapped[bool]
    verified_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    disabled: Mapped[bool] = mapped_column(default=False)
    disabled_timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    user: Mapped['User'] = relationship(back_populates='emails')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(\n'
            f'    email_id={self.email_id},\n'
            f'    user_id={self.user_id},\n'
            f'    email={self.email},\n'
            f'    is_primary={self.is_primary},\n'
            f'    verified_at={self.verified_at},\n'
            f'    disabled={self.disabled},\n'
            f'    disabled_timestamp={self.disabled_timestamp},\n)'
        )


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

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(\n'
            f'    user_sign_in_id={self.user_sign_in_id},\n'
            f'    user_id={self.user_id},\n'
            f'    sign_in_timestamp={self.sign_in_timestamp},\n'
            f'    success={self.success},\n'
            f'    origin={self.origin},\n'
            f'    device={self.device},\n'
            f'    country={self.country},\n'
            f'    credential_nickname={self.credential_nickname},\n'
            f'    credential_id={self.credential_id},\n'
            f'    sign_in_type={self.sign_in_type},\n'
            f'    rp_id={self.rp_id},\n)'
        )


Index(f'{UserSignIn.__tablename__}_ix1', UserSignIn.user_id, UserSignIn.sign_in_timestamp)
Index(f'{UserSignIn.__tablename__}_ix2', UserSignIn.origin)

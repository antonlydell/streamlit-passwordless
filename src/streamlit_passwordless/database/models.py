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
        The active directory username of the user is such exists.

    displayname : Optional[str]
        A descriptive name of the user that is easy to understand for a human.

    disabled : bool, default False
        If False the user is enabled and if True the user is disabled.
        A disabled user is not able to register credentials or sign in.

    disabled_timestamp : Optional[datetime]
        The timestamp when the user was disabled.

    emails : list[Email]
        The email addresses associated with the user.
    """

    __tablename__ = 'stp_user'

    user_id: Mapped[str] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    ad_username: Mapped[Optional[str]]
    displayname: Mapped[Optional[str]]
    disabled: Mapped[bool] = mapped_column(default=False)
    disabled_timestamp: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP())
    emails: Mapped[list['Email']] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(\n'
            f'    user_id={self.user_id},\n'
            f'    username={self.username},\n'
            f'    ad_username={self.username},\n'
            f'    displayname={self.displayname},\n'
            f'    disabled={self.disabled},\n'
            f'    disabled_timestamp={self.disabled},\n'
            f'    emails={len(self.emails)}\n)'
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

    active : bool, default False
        If the email address is active or not.

    user : User
        The user object the email address belongs to.
    """

    __tablename__ = 'stp_email'

    email_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(User.user_id))
    email: Mapped[str] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(default=True)
    user: Mapped['User'] = relationship(back_populates='emails')

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(\n'
            f'    email_id={self.email_id},\n'
            f'    user_id={self.user_id},\n'
            f'    email={self.email},\n'
            f'    active={self.active},\n)'
        )


Index(f'{Email.__tablename__}_email_ix', Email.email)
Index(f'{Email.__tablename__}_user_id_ix', Email.user_id)

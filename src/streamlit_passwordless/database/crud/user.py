r"""Database operations on the user table."""

# Standard library
from typing import Sequence

# Third party
import pandas as pd
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

# Local
from streamlit_passwordless import exceptions

from .. import models
from ..core import Session
from ..schemas import user as schemas


def get_all_users(
    session: Session,
    skip: int = 0,
    limit: int | None = None,
    as_df: bool = False,
    index_col: str = 'user_id',
) -> pd.DataFrame | Sequence[models.User]:
    r"""Get all users from the database.

    Parameters
    ----------
    session : Session
        An active database session.

    skip : int, default 0
        The number of users to skip from the beginning of the result set.
        The users are order by their username.

    limit : int or None, default None
        Limit the result to desired number of users. If None all users are returned.

    as_df : bool, default False
        Return the users as a :class:`pandas.DataFrame` instead of a sequence of user models.

    index_col : str, default 'user_id'
        The column from the user table to use as the index column
        of the :class:`pandas.DataFrame` if `as_df` is True.

    Returns
    -------
    pandas.DataFrame or Sequence[streamlit_passwordless.db.models.User]
        The users from the database.
    """

    query = select(models.User).order_by(models.User.username).offset(skip).limit(limit)

    if as_df:
        return pd.read_sql_query(sql=query, con=session.bind, index_col=index_col)  # type: ignore
    else:
        return session.scalars(query).all()


def get_user_by_username(
    session: Session, username: str, disabled: bool = False
) -> models.User | None:
    r"""Get a user by its username.

    Parameters
    ----------
    session : Session
        An active database session.

    username : str
        The username to filter by.

    disabled : bool, default False
        True if filtering for a disabled user and False for an active user.

    Returns
    -------
    streamlit_passwordless.db.models.User or None
        The user with `username` or None if a user with `username` was not found.
    """

    query = select(models.User).where(
        and_(models.User.username == username, models.User.disabled == disabled)
    )
    return session.scalars(query).one_or_none()


def get_user_by_user_id(
    session: Session, user_id: str, disabled: bool = False, is_verified: bool | None = None
) -> models.User | None:
    r"""Get a user by user_id.

    Parameters
    ----------
    session : Session
        An active database session.

    user_id : str
        The user_id to filter by.

    disabled : bool, default False
        True if filtering for a disabled user and False for an active user.

    is_verified : bool or None, default None
        If True filter by verified users and if False by non-verified users.
        If None filtering by verified users is omitted.

    Returns
    -------
    streamlit_passwordless.db.models.User or None
        The user matching `user_id` or None if a user with `user_id` was not found.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the user from the database.
    """

    query = select(models.User).where(
        and_(models.User.user_id == user_id, models.User.disabled == disabled)
    )
    if is_verified is True:
        query = query.where(models.User.verified_at._is_not(None))
    elif is_verified is False:
        query = query.where(models.User.verified_at._is(None))
    else:
        pass

    try:
        return session.scalars(query).one_or_none()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError(
            f'Error loading user {user_id=} from database!', e=e
        ) from None


def create_user(session: Session, user: schemas.UserCreate) -> models.User:
    r"""Create a new user.

    The user is added to the session and will be persisted in the
    database when the method `session.commit` is executed.

    Parameters
    ----------
    session : Session
        An active database session.

    user : schemas.UserCreate
        The user to crete.

    Returns
    -------
    streamlit_passwordless.db.models.User
        The database model of the created user.
    """

    db_user = models.User(**user.model_dump())
    session.add(db_user)

    return db_user

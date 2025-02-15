r"""Database operations on the user table."""

# Standard library
import logging
from typing import Sequence

# Third party
import pandas as pd
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.crud.custom_role import get_custom_roles
from streamlit_passwordless.models import User

from .. import models
from ..core import Session
from ..core import commit as db_commit

logger = logging.getLogger(__name__)


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
    session: Session, username: str, disabled: bool | None = False
) -> models.User | None:
    r"""Get a user by its username.

    Parameters
    ----------
    session : Session
        An active database session.

    username : str
        The username to filter by.

    disabled : bool or None, default False
        True if filtering for a disabled user and False for an enabled user.
        If None filtering by disabled or enabled user is omitted.

    Returns
    -------
    streamlit_passwordless.db.models.User or None
        The user with `username` or None if a user with `username` was not found.
    """

    if disabled is None:
        where_clause = models.User.username == username
    else:
        where_clause = and_(models.User.username == username, models.User.disabled == disabled)

    query = select(models.User).where(where_clause)

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


def create_user(session: Session, user: User, commit: bool = False) -> models.User:
    r"""Create a new user in the database.

    Parameters
    ----------
    session : Session
        An active database session.

    user : streamlit_passwordless.User
        The user to create.

    commit : bool, default False
        True if the added user should be committed after being added to the session and False
        to commit later. Note that the returned `db_user` object will be in a expired state
        if committing and will be re-loaded from the database upon next access.

    Returns
    -------
    db_user : streamlit_passwordless.db.models.User
        The database model of the created user.

    Raises
    ------
    streamlit_passwordless.DatabaseCreateUserError
        If an error occurs while saving the user to the database or if the
        role of the user does not exist in the database.
    """

    if (role_id := user.role.role_id) is None:
        error_msg = (
            f'Cannot create user "{user.username}" because user.role.role_id is not specified!'
        )
        logger.error(error_msg)
        raise exceptions.DatabaseCreateUserError(error_msg)

    db_user = models.User(
        user_id=user.user_id,
        username=user.username,
        ad_username=user.ad_username,
        displayname=user.displayname,
        role_id=role_id,
        verified_at=user.verified_at,
        disabled=user.disabled,
        disabled_timestamp=user.disabled_timestamp,
    )

    if emails := user.emails:
        db_emails = [models.Email(**email.model_dump()) for email in emails]
        db_user.emails.extend(db_emails)
        session.add_all(db_emails)

    if custom_roles := user.custom_roles:
        role_ids = {role_id for cr in custom_roles.values() if (role_id := cr.role_id) is not None}
        db_custom_roles = get_custom_roles(session=session, role_ids=role_ids)
        db_user.custom_roles = {model.name: model for model in db_custom_roles}

    session.add(db_user)

    if commit:
        error_msg = (
            f'Unable to save user "{user.username}" to database! Check the logs for more details.'
        )
        try:
            db_commit(session=session, error_msg=error_msg)
        except exceptions.DatabaseError as e:
            logger.error(e.detailed_message)
            raise exceptions.DatabaseCreateUserError(error_msg, e=e) from None

    return db_user

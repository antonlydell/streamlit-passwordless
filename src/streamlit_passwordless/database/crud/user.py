r"""Database operations on the user table."""

# Standard library
import logging
from collections.abc import Sequence
from typing import Literal, overload

# Third party
import pandas as pd
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    LoaderCriteriaOption,
    joinedload,
    raiseload,
    selectinload,
    undefer_group,
    with_loader_criteria,
)
from sqlalchemy.orm.interfaces import LoaderOption

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.database.core import Session
from streamlit_passwordless.database.core import commit as db_commit
from streamlit_passwordless.database.crud.custom_role import get_custom_roles
from streamlit_passwordless.database.models import (
    AUDIT_COLUMNS_GROUP,
    CustomRole,
    Email,
    Role,
    User,
    UserID,
)

logger = logging.getLogger(__name__)


def _configure_user_relationship_loading(
    load_role: bool = True,
    load_custom_roles: bool = False,
    load_emails: bool = False,
    raiseload_if_unloaded: bool = True,
    defer_role_description: bool = True,
    undefer_audit_columns: bool = False,
    audit_columns_group_name: str = AUDIT_COLUMNS_GROUP,
) -> list[LoaderOption | LoaderCriteriaOption]:
    r"""Configure how the user relationships should be loaded.

    Parameters
    ----------
    load_role : bool, default True
        True if the role of the user should be loaded and False otherwise.

    load_custom_roles : bool, default False
        True if the custom roles of the user should be loaded and False otherwise.

    load_emails : bool, default False
        True if the enabled emails of the user should be loaded and False otherwise.

    raiseload_if_unloaded : bool, default True
        If True :exc:`sqlalchemy.exc.InvalidRequestError` is raised if trying to access an
        unloaded object (role, custom_roles or emails) of the user. When False the objects
        are lazy loaded on access.

    defer_role_description : bool, default True
        True if the description columns of the role and custom_roles should not be loaded
        and False otherwise. A :exc:`sqlalchemy.exc.InvalidRequestError` will be raised
        when trying to access these columns if `raiseload_if_unloaded` is True.

    undefer_audit_columns : bool, default False
        True if the audit columns should be undeferred and loaded and False to not load the columns.

    audit_columns_group_name : str, default streamlit_passwordless.db.AUDIT_COLUMNS_GROUP
        The name of the audit columns' group to undefer through `undefer_audit_columns`.

    Returns
    -------
    options : list[sqlalchemy.orm.interfaces.LoaderOption | sqlalchemy.orm.LoaderCriteriaOption]
        The options to apply to the query.

    Raises
    ------
    sqlalchemy.exc.InvalidRequestError
        If a deferred object or column is accessed when `raiseload_if_unloaded` is True.
    """

    options: list[LoaderOption | LoaderCriteriaOption] = []

    if undefer_audit_columns:  # undefer for User
        options.append(undefer_group(audit_columns_group_name))

    if load_role:
        role_loader = joinedload(User.role)
        if defer_role_description:
            role_loader = role_loader.defer(Role.description, raiseload=raiseload_if_unloaded)
        if undefer_audit_columns:
            role_loader = role_loader.undefer_group(audit_columns_group_name)
        options.append(role_loader)

    elif raiseload_if_unloaded:
        options.append(raiseload(User.role))

    if load_custom_roles:
        custom_roles_loader = selectinload(User.custom_roles)
        if defer_role_description:
            custom_roles_loader = custom_roles_loader.defer(
                CustomRole.description, raiseload=raiseload_if_unloaded
            )
        if undefer_audit_columns:
            custom_roles_loader = custom_roles_loader.undefer_group(audit_columns_group_name)
        options.append(custom_roles_loader)

    elif raiseload_if_unloaded:
        options.append(raiseload(User.custom_roles))

    if load_emails:
        emails_loader = selectinload(User.emails)
        if undefer_audit_columns:
            emails_loader = emails_loader.undefer_group(audit_columns_group_name)
        options.append(emails_loader)
        options.append(
            with_loader_criteria(
                Email,
                Email.disabled.is_(False),
                include_aliases=True,
            )
        )

    elif raiseload_if_unloaded:
        options.append(raiseload(User.emails))

    return options


@overload
def get_all_users(
    session: Session,
    skip: int = 0,
    limit: int | None = None,
    as_df: Literal[False] = False,
    index_col: str = 'user_id',
) -> Sequence[User]: ...


@overload
def get_all_users(
    session: Session,
    skip: int = 0,
    limit: int | None = None,
    as_df: Literal[True] = True,
    index_col: str = 'user_id',
) -> pd.DataFrame: ...


def get_all_users(
    session: Session,
    skip: int = 0,
    limit: int | None = None,
    as_df: bool = False,
    index_col: str = 'user_id',
) -> pd.DataFrame | Sequence[User]:
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

    query = select(User).order_by(User.username).offset(skip).limit(limit)

    if as_df:
        return pd.read_sql_query(sql=query, con=session.bind, index_col=index_col)  # type: ignore
    return session.scalars(query).all()


def get_user_by_username(
    session: Session, username: str, disabled: bool | None = False
) -> User | None:
    r"""Get a user by its username.

    Parameters
    ----------
    session : Session
        An active database session.

    username : str
        The username to filter by.

    disabled : bool or None, default False
        True if filtering for a disabled user and False for an enabled user.
        If None filtering by a disabled or enabled user is omitted.

    Returns
    -------
    streamlit_passwordless.db.models.User or None
        The user with `username` or None if a user with `username` was not found.
    """

    if disabled is None:
        where_clause = User.username == username
    else:
        where_clause = and_(User.username == username, User.disabled == disabled)

    query = select(User).where(where_clause)

    return session.scalars(query).one_or_none()


def get_user_by_user_id(
    session: Session,
    user_id: UserID,
    disabled: bool | None = False,
    is_verified: bool | None = None,
    load_role: bool = True,
    load_custom_roles: bool = False,
    load_emails: bool = False,
    raiseload: bool = True,
    defer_role_description: bool = True,
    undefer_audit_columns: bool = False,
    audit_columns_group_name: str = AUDIT_COLUMNS_GROUP,
) -> User | None:
    r"""Get a user by user_id.

    Parameters
    ----------
    session : streamlit_passwordless.db.Session
        An active database session.

    user_id : streamlit_passwordless.UserID
        The user_id to filter by.

    disabled : bool or None, default False
        True if filtering for a disabled user and False for an active user.
        If None filtering by a disabled or enabled user is omitted.

    is_verified : bool or None, default None
        If True filter by verified users and if False by non-verified users.
        If None filtering by verified users is omitted.

    load_role : bool, default True
        True if the role of the user should be loaded and False otherwise.

    load_custom_roles : bool, default False
        True if the custom roles of the user should be loaded and False otherwise.

    load_emails : bool, default False
        True if the enabled emails of the user should be loaded and False otherwise.

    raiseload : bool, default True
        If True :exc:`sqlalchemy.exc.InvalidRequestError` is raised if trying to access an
        unloaded object (role, custom_roles or emails) of the user. When False the objects
        are lazy loaded on access.

    defer_role_description : bool, default True
        True if the description columns of the role and custom_roles should not be loaded
        and False otherwise. A :exc:`sqlalchemy.exc.InvalidRequestError` will be raised
        when trying to access these columns if `raiseload` is True.

    undefer_audit_columns : bool, default False
        True if the audit columns should be undeferred and loaded and False to not load the columns.

    audit_columns_group_name : str, default streamlit_passwordless.db.AUDIT_COLUMNS_GROUP
        The name of the audit columns' group to undefer through `undefer_audit_columns`.

    Returns
    -------
    streamlit_passwordless.db.models.User or None
        The user matching `user_id` or None if a user with `user_id` was not found.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the user from the database.

    sqlalchemy.exc.InvalidRequestError
        If a deferred object or column is accessed when `raiseload` is True.
    """

    query = select(User)
    options = _configure_user_relationship_loading(
        load_role=load_role,
        load_custom_roles=load_custom_roles,
        load_emails=load_emails,
        raiseload_if_unloaded=raiseload,
        defer_role_description=defer_role_description,
        undefer_audit_columns=undefer_audit_columns,
        audit_columns_group_name=audit_columns_group_name,
    )
    query = query.options(*options)

    if disabled is None:
        where_clause = User.user_id == user_id
    else:
        where_clause = and_(User.user_id == user_id, User.disabled == disabled)

    query = query.where(where_clause)

    if is_verified is True:
        query = query.where(User.verified_at.is_not(None))
    elif is_verified is False:
        query = query.where(User.verified_at.is_(None))
    else:
        pass

    try:
        return session.scalars(query).one_or_none()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError(
            f'Error loading user {user_id=} from database!', e=e
        ) from None


def create_user(
    session: Session,
    user: models.User,
    custom_roles: Sequence[models.CustomRole] | None = None,
    created_by_user_id: UserID | None = None,
    commit: bool = False,
) -> User:
    r"""Create a new user in the database.

    Parameters
    ----------
    session : streamlit_passwordless.db.Session
        An active database session.

    user : streamlit_passwordless.User
        The user to create.

    custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole] or None, default None
        The custom roles from the active database `session` to associate with the user.
        If provided these roles will take precedence over the custom roles defined on
        `user` and avoids a database lookup since the custom roles already exist in the `session`.

    created_by_user_id : streamlit_passwordless.UserID or None, default None
        The ID of the user that is creating the new user.

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

    db_user = User(
        user_id=user.user_id,
        username=user.username,
        ad_username=user.ad_username,
        displayname=user.displayname,
        role_id=role_id,
        verified_at=user.verified_at,
        disabled=user.disabled,
        disabled_at=user.disabled_at,
        created_by=created_by_user_id,
    )

    if emails := user.emails:
        db_emails = [Email(**email.model_dump()) for email in emails]
        db_user.emails.extend(db_emails)
        session.add_all(db_emails)

    if custom_roles:
        db_user.custom_roles = {model.role_id: model for model in custom_roles}
    elif _custom_roles := user.custom_roles:
        db_custom_roles = get_custom_roles(session=session, role_ids=_custom_roles.keys())
        db_user.custom_roles = {model.role_id: model for model in db_custom_roles}

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

r"""Database operations on the role table (:class:`streamlit_passwordless.db.models.Role`)."""

# Standard library
from typing import Sequence

# Third party
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.core import Session
from streamlit_passwordless.database.core import commit as db_commit
from streamlit_passwordless.database.models import Role
from streamlit_passwordless.database.schemas.role import RoleCreate


def get_all_roles(
    session: Session,
    skip: int = 0,
    limit: int | None = None,
    as_df: bool = False,
    index_col: str = 'role_id',
) -> pd.DataFrame | Sequence[Role]:
    r"""Get all roles from the database.

    Parameters
    ----------
    session : Session
        An active database session.

    skip : int, default 0
        The number of roles to skip from the beginning of the result set.
        The roles are order by their rank.

    limit : int or None, default None
        Limit the result to desired number of roles. If None all roles are returned.

    as_df : bool, default False
        Return the roles as a :class:`pandas.DataFrame` instead of a sequence of role models.

    index_col : str, default 'role_id'
        The column from the role table to use as the index column
        of the :class:`pandas.DataFrame` if `as_df` is True.

    Returns
    -------
    pandas.DataFrame or Sequence[streamlit_passwordless.db.models.Role]
        The roles from the database.
    """

    query = select(Role).order_by(Role.rank).offset(skip).limit(limit)

    if as_df:
        return pd.read_sql_query(sql=query, con=session.bind, index_col=index_col)  # type: ignore
    else:
        return session.scalars(query).all()


def get_role_by_name(session: Session, name: str) -> Role | None:
    r"""Get a role by its unique name.

    Parameters
    ----------
    session : Session
        An active database session.

    name : str
        The name of the role to filter by.

    Returns
    -------
    streamlit_passwordless.db.models.Role or None
        The role matching `name` or None if a role with `name` was not found.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the role from the database.
    """

    query = select(Role).where(Role.name == name)
    try:
        return session.scalars(query).one_or_none()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError(f'Error loading role {name=} from database!', e=e) from None


def get_role_by_role_id(session: Session, role_id: int) -> Role | None:
    r"""Get a role by role_id.

    Parameters
    ----------
    session : Session
        An active database session.

    role_id : int
        The role_id to filter by.

    Returns
    -------
    streamlit_passwordless.db.models.Role or None
        The role matching `role_id` or None if a role with `role_id` was not found.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the role from the database.
    """

    query = select(Role).where(Role.role_id == role_id)
    try:
        return session.scalars(query).one_or_none()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError(
            f'Error loading role {role_id=} from database!', e=e
        ) from None


def create_role(session: Session, role: RoleCreate, commit: bool = False) -> Role:
    r"""Create a new role in the database.

    Parameters
    ----------
    session : Session
        An active database session.

    role : streamlit_passwordless.db.RoleCreate
        The schema of the role to create.

    commit : bool, default False
        True if the added role should be committed after being added to the session and False
        to commit later. Note that the returned `db_role` object will be in a expired state
        if committing and will be re-loaded from the database upon next access.

    Returns
    -------
    db_role : streamlit_passwordless.db.models.Role
        The database model of the created role.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while saving the role to the database.

    streamlit_passwordless.DatabaseStatementError
        If there is an error with the executed SQL statement.
    """

    db_role = Role(**role.model_dump())
    session.add(db_role)

    if commit:
        error_msg = f'Unable to save role {role.name} to database! Check the logs for more details.'
        db_commit(session=session, error_msg=error_msg)

    return db_role


def create_default_roles(session: Session, commit: bool = False) -> tuple[Role, ...]:
    r"""Create the default roles in the database.

    Parameters
    ----------
    session : Session
        An active database session.

    commit : bool, default False
        if True the default roles are committed to the database after being added
        to the session. If False (the default) they are only added to the session.

    Returns
    -------
    roles : tuple[streamlit_passwordless.db.models.Role, ...]
        The created default roles.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while saving the roles to the database.

    streamlit_passwordless.DatabaseStatementError
        If there is an error with the executed SQL statement.
    """

    roles = (Role.create_viewer(), Role.create_user(), Role.create_superuser(), Role.create_admin())
    session.add_all(roles)

    if commit:
        error_msg = (
            f'Unable to save default roles: {", ".join(r.name for r in roles)} to the database!\n'
            'Check the logs for more details.'
        )
        db_commit(session=session, error_msg=error_msg)

    return roles

r"""Database operations on the stp_custom_role table."""

# Standard library
from typing import Iterable, Sequence

# Third party
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.database.core import Session
from streamlit_passwordless.database.core import commit as db_commit
from streamlit_passwordless.database.models import CustomRole


def get_all_custom_roles(
    session: Session,
    skip: int = 0,
    limit: int | None = None,
    as_df: bool = False,
    index_col: str | list[str] | None = 'role_id',
) -> pd.DataFrame | Sequence[CustomRole]:
    r"""Get all custom roles from the database.

    Parameters
    ----------
    session : Session
        An active database session.

    skip : int, default 0
        The number of custom roles to skip from the beginning of the result set.
        The custom roles are order by their rank.

    limit : int or None, default None
        Limit the result to desired number of custom roles. If None all custom roles are returned.

    as_df : bool, default False
        If True return the custom roles as a :class:`pandas.DataFrame` instead of a sequence
        of :class:`streamlit_passwordless.db.models.CustomRole`.

    index_col : str or list[str] or None, default 'role_id'
        The column from the table stp_custom_role to use as the index column of the
        :class:`pandas.DataFrame` if `as_df` is True. Specify a list of column names
        to create a multiindex. If None no column is added to the index.

    Returns
    -------
    pandas.DataFrame or Sequence[streamlit_passwordless.db.models.CustomRole]
        The custom roles from the database.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the custom roles from the database.
    """

    query = select(CustomRole).order_by(CustomRole.rank).offset(skip).limit(limit)

    try:
        if as_df:
            return pd.read_sql_query(sql=query, con=session.bind, index_col=index_col)  # type: ignore
        else:
            return session.scalars(query).all()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError('Error loading custom roles from database!', e=e) from None


def get_custom_roles(
    session: Session, role_ids: Iterable[int] | None = None, names: Iterable[str] | None = None
) -> Sequence[CustomRole]:
    r"""Get custom roles by `role_ids` or unique `names`.

    Either the `role_ids` or `names` parameter must be specified,
    where `role_ids` will take precedence over `names`.

    Parameters
    ----------
    session : Session
        An active database session.

    role_id : Iterable[int] or None, default None
        The role_id:s of the custom roles to filter by.

    name : Iterable[str] or None, default None
        The names of the custom roles to filter by.

    Returns
    -------
    Sequence[streamlit_passwordless.db.models.CustomRole]
        The custom roles matching `role_ids` or `names`.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the custom roles from the database.
    """

    if role_ids is not None:
        where_clause = CustomRole.role_id.in_(role_ids)
    elif names is not None:
        where_clause = CustomRole.name.in_(names)
    else:
        raise exceptions.StreamlitPasswordlessError(
            'Either "role_ids" or "names" parameter must be specified!'
        )

    try:
        return session.scalars(select(CustomRole).where(where_clause)).all()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError('Error loading custom roles from database!', e=e) from None


def create_custom_role(
    session: Session, role: models.CustomRole, commit: bool = False
) -> CustomRole:
    r"""Create a new custom role in the database.

    Parameters
    ----------
    session : Session
        An active database session.

    role : streamlit_passwordless.CustomRole
        The custom role to create.

    commit : bool, default False
        True if the added custom role should be committed after being added to the session and
        False to commit later. Note that the returned `db_role` object will be in a expired state
        if committing and will be re-loaded from the database upon next access.

    Returns
    -------
    db_role : streamlit_passwordless.db.models.CustomRole
        The database model of the created custom role.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while saving the custom role to the database.

    streamlit_passwordless.DatabaseStatementError
        If there is an error with the executed SQL statement.
    """

    db_role = CustomRole(**role.model_dump())
    session.add(db_role)

    if commit:
        error_msg = (
            f'Unable to save custom role "{role.name}" to database! '
            'Check the logs for more details.'
        )
        db_commit(session=session, error_msg=error_msg)

    return db_role

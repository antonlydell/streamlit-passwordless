r"""The application logic of the admin app."""

# Standard library
from typing import Sequence

# Third party
import pandas as pd
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.session_state import (
    SK_DB_CUSTOM_ROLES,
    SK_DB_ROLES,
    SK_SELECTABLE_USERS_DATAFRAME,
)


def get_selectable_users_from_database(db_session: db.Session) -> pd.DataFrame:
    r"""Load the selectable users from the database.

    Updates the session state key
    :attr:`streamlit_passwordless.app.components.keys.SK_SELECTABLE_USERS_DATAFRAME`
    with the function result.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    Returns
    -------
    pandas.DataFrame
        The selectable users.
    """

    df = db.get_all_users(session=db_session, as_df=True)
    st.session_state[SK_SELECTABLE_USERS_DATAFRAME] = df

    return df


def get_all_roles_from_database(db_session: db.Session) -> Sequence[db.models.Role]:
    r"""Load the user roles from the database.

    Updates the session state key
    :attr:`streamlit_passwordless.app.components.keys.SK_DB_ROLES`
    with the function result.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    Returns
    -------
    roles : Sequence[streamlit_passwordless.db.models.Role]
        The user roles.
    """

    roles = db.get_all_roles(session=db_session, as_df=False)
    st.session_state[SK_DB_ROLES] = roles

    return roles


def get_all_custom_roles_from_database(db_session: db.Session) -> Sequence[db.models.CustomRole]:
    r"""Load the user custom roles from the database.

    Updates the session state key
    :attr:`streamlit_passwordless.app.components.keys.SK_DB_CUSTOM_ROLES`
    with the function result.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    Returns
    -------
    custom_roles : Sequence[streamlit_passwordless.db.models.Role]
        The user custom roles.
    """

    custom_roles = db.get_all_custom_roles(session=db_session, as_df=False)
    st.session_state[SK_DB_CUSTOM_ROLES] = custom_roles

    return custom_roles


def load_users_and_roles_from_database(
    db_session: db.Session,
) -> tuple[pd.DataFrame, Sequence[db.models.Role], Sequence[db.models.CustomRole]]:
    r"""Load the selectable users, roles and custom roles from the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    Returns
    -------
    df_users : pandas.DataFrame
        The selectable users.

    roles : Sequence[streamlit_passwordless.db.models.Role]
        The user roles.

    custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole]
        The user custom roles.
    """

    if st.session_state.get(SK_SELECTABLE_USERS_DATAFRAME) is None:
        get_selectable_users_from_database(db_session=db_session)
    df_users = st.session_state.get(SK_SELECTABLE_USERS_DATAFRAME, pd.DataFrame())

    if st.session_state.get(SK_DB_ROLES) is None:
        get_all_roles_from_database(db_session=db_session)
    roles = st.session_state.get(SK_DB_ROLES, [])

    if st.session_state.get(SK_DB_CUSTOM_ROLES) is None:
        get_all_custom_roles_from_database(db_session=db_session)
    custom_roles = st.session_state.get(SK_DB_CUSTOM_ROLES, [])

    return df_users, roles, custom_roles


def filter_selectable_users(
    df: pd.DataFrame, disabled: bool | None, roles: set[int]
) -> pd.DataFrame:
    r"""Filter the selectable users.

    Parameters
    ----------
    df : pandas.DataFrame
        The selectable users.

    disabled : bool or None
        Filter by disabled (True) or enabled (False) users.
        If None filtering by disabled/enabled is omitted.

    roles : set[int]
        The role_id:s of the user roles to filter by.

    Returns
    -------
    pandas.DataFrame
        The selectable users after filtering by disabled/enabled and roles.
    """

    if disabled is None:
        if roles:
            return df.loc[df['role_id'].isin(roles), :]
        else:
            return df
    else:
        disabled_filter = df['disabled'].eq(disabled)
        if roles:
            roles_filter = df['role_id'].isin(roles)
            return df.loc[disabled_filter & roles_filter, :]
        else:
            return df.loc[disabled_filter, :]

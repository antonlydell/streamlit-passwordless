r"""The database functions that are cached by Streamlit."""

# Standard library

# Third party
import streamlit as st

# Local
from . import core


@st.cache_resource()
def create_session_factory(
    url: core.URL,
    autoflush: bool = False,
    expire_on_commit: bool = False,
    create_database: bool = True,
    **engine_config,
) -> core.SessionFactory:
    r"""Create the database session factory, which can produce database sessions.

    The database engine is bound to each session produced by the factory.

    Parameters
    ----------
    url : str or sqlalchemy.URL
        The SQLAlchemy database url.

    autoflush : bool, default False
        Automatically flush pending changes within the session to the database
        before executing new SQL statements.

    expire_on_commit : bool, default False
        If True make the connection between the models and the database expire after a
        transaction within a session has been committed and if False make the database models
        accessible after the commit.

    create_database : bool, default True
        If True the database table schema will be created if it does not exist.

    **engine_config : dict
        Additional keyword arguments passed to the :func:`sqlalchemy.create_engine` function.

    Returns
    -------
    session_factory : streamlit_passwordless.db.SessionFactory
        The session factory that can produce new database sessions.
    """

    session_factory, engine = core.create_session_factory(
        url=url,
        autoflush=autoflush,
        expire_on_commit=expire_on_commit,
        create_database=create_database,
        **engine_config,
    )

    return session_factory

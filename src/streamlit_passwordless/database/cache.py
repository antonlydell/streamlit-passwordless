r"""The database functions that are cached by Streamlit."""

# Standard library
import logging

# Third party
import streamlit as st

# Local
from streamlit_passwordless import exceptions

from . import core
from .crud.role import create_default_roles

logger = logging.getLogger(__name__)

create_session_factory_cached = st.cache_resource(core.create_session_factory)


@st.cache_resource()
def init(_session: core.Session) -> tuple[bool, str]:
    r"""Initialize a database with the required data.

    The default roles of Streamlit Passwordless are created in the database.

    Parameters
    ----------
    _session : streamlit_passwordless.db.Session
        An active database session.

    Returns
    -------
    error : bool
        True if a :exc:`streamlit_passwordless.DatabaseError` occurred and the database
        could not be initialized correctly and False for no error.

    error_msg : str
        An error message that is safe to display to the user. An empty
        string is returned if `error` is False.
    """

    error = False
    error_msg = ''
    try:
        create_default_roles(session=_session, commit=True)
    except exceptions.DatabaseError as e:
        error = True
        error_msg = e.displayable_message
        logger.warning(e.detailed_message)
        _session.rollback()

    return error, error_msg

r"""The views of the init page."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.components.config import ICON_SUCCESS, ICON_WARNING


def title() -> None:
    r"""Render the title view of the init page."""

    st.title('Initialize Streamlit Passwordless')
    st.divider()


def initialize(db_session: db.Session, db_url: db.URL) -> None:
    r"""Render the initialize view of the init page.

    Initialize the database by creating the user roles and
    warn the user if the database is already initialized.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the database to initialize.

    db_url : streamlit_passwordless.db.URL
        The database url of the database being initialized.
    """

    error, error_msg = db.init(_session=db_session)
    if error:
        message = f'Database "{db_url}" already initialized! {error_msg}'
        st.warning(message, icon=ICON_WARNING)
    else:
        st.success(f'Successfully initialized database : "{db_url}"!', icon=ICON_SUCCESS)

    st.divider()

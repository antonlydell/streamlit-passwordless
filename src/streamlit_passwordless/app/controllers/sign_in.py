r"""The controller of the sign in page."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.config import Pages
from streamlit_passwordless.app.views.sign_in import title
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.components import bitwarden_sign_in_button
from streamlit_passwordless.models import AdminRole


def controller(client: BitwardenPasswordlessClient, db_session: db.Session) -> None:
    r"""Render the sign in page.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.
    """

    banner_container = st.empty()

    with st.container(border=True):
        title()
        bitwarden_sign_in_button(
            client=client,
            db_session=db_session,
            role=AdminRole,
            banner_container=banner_container,
            redirect=Pages.ADMIN,
        )

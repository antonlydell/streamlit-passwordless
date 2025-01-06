r"""The controller of the admin page."""

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.views.admin import title
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient


def controller(client: BitwardenPasswordlessClient, db_session: db.Session) -> None:
    r"""Render the admin page.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.
    """

    title()

r"""The controller of the admin page."""

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.views.admin import sidebar, title
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.models import User


def controller(client: BitwardenPasswordlessClient, db_session: db.Session, user: User) -> None:
    r"""Render the admin page.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    user : streamlit_passwordless.User
        The signed in admin user.
    """

    title()
    sidebar(user=user)

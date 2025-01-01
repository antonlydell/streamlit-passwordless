r"""The controller of the init page."""

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.config import ConfigManager
from streamlit_passwordless.app.views.init import initialize, title
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient


def controller(
    cm: ConfigManager, db_session: db.Session, client: BitwardenPasswordlessClient
) -> None:
    r"""Render the init page.

    Parameters
    ----------
    cm : streamlit_passwordless.ConfigManager
        The loaded configuration of the application.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.
    """

    title()
    initialize(db_session=db_session, db_url=cm.db_url)

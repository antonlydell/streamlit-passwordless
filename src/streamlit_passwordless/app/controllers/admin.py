r"""The controller of the admin page."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.logic.admin import load_users_and_roles_from_database
from streamlit_passwordless.app.views.admin import manage_users_view, sidebar, title
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
    users_tab, roles_tab, custom_roles_tab = st.tabs(('Users', 'Roles', 'Custom Roles'))

    df_users, roles, custom_roles = load_users_and_roles_from_database(db_session=db_session)

    with users_tab:
        manage_users_view(
            df=df_users,
            roles=roles,
            custom_roles=custom_roles,
            client=client,
            db_session=db_session,
        )
    with roles_tab:
        pass
    with custom_roles_tab:
        pass

r"""The views of the init page."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.components import (
    bitwarden_register_form,
    bitwarden_register_form_existing_user,
    bitwarden_sign_in_form,
)
from streamlit_passwordless.components.config import ICON_SUCCESS, ICON_WARNING
from streamlit_passwordless.models import Role


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


def create_admin_user(db_session: db.Session, client: BitwardenPasswordlessClient) -> None:
    r"""Render the create admin user view of the init page.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the database to initialize.

    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the Bitwarden Passwordless backend API.
    """

    left_col, right_col = st.columns(2)
    with left_col:
        user, _ = bitwarden_register_form(
            client=client,
            db_session=db_session,
            role=Role.create_admin(),
            with_displayname=True,
            with_credential_nickname=True,
            with_discoverability=True,
            title='Register an admin user',
        )

    username = user.username if user is not None else ''
    with right_col:
        bitwarden_sign_in_form(client=client, db_session=db_session, with_alias=False)
        bitwarden_register_form_existing_user(
            client=client,
            db_session=db_session,
            with_discoverability=True,
            title=f'Register additional passkeys for user : {username}',
        )

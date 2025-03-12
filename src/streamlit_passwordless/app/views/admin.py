r"""The views of the admin page."""

# Standard library
from typing import Sequence

# Third party
import pandas as pd
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.components.admin import (
    create_user_button,
    delete_user_button,
    refresh_users_button,
    user_role_multiselect,
    user_selectbox,
    user_state_radio_button,
)
from streamlit_passwordless.app.logic.admin import filter_selectable_users
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.components import (
    BannerMessageType,
    bitwarden_register_form_existing_user,
    display_banner_message,
)
from streamlit_passwordless.components.sign_out import sign_out_button
from streamlit_passwordless.models import User


def title() -> None:
    r"""Render the title view of the admin page."""

    st.title('Streamlit Passwordless Admin Console')
    st.divider()


def sidebar(user: User) -> None:
    r"""Render the sidebar of the admin page.

    Parameters
    ----------
    user : streamlit_passwordless.User
        The signed in admin user.
    """

    sign_in = user.sign_in
    if sign_in is None:
        return None

    username = user.username if (dn := user.displayname) is None else dn

    user_info = f"""\
- **User :** {username} ({user.role.name})
- **Signed in at :** {sign_in.sign_in_timestamp.strftime(r'%Y-%m-%d %H:%M:%S %Z')}
- **Passkey :** {sign_in.credential_nickname}
"""

    with st.sidebar:
        sign_out_button(user=user)
        st.markdown(user_info)


def statistics_view(nr_users_database: int, nr_users_bwp: int, nr_passkeys: int) -> None:
    r"""The statistics view of the admin page.

    Display the number of users and the number of registered passkeys.

    Parameters
    ----------
    nr_users_database : int
        The number of users in the database.

    nr_users_bwp : int
        The number of registered users in Bitwarden Passwordless.dev.

    nr_passkeys : int
        The number of registered passkeys in Bitwarden Passwordless.dev.
    """

    nr_local_users_col, nr_bwp_users_col, nr_passkeys_col = st.columns([0.3, 0.4, 0.3])
    with nr_local_users_col:
        st.metric(label='Users in Database', value=nr_users_database)
    with nr_bwp_users_col:
        st.metric(label='Users Bitwarden Passwordless', value=nr_users_bwp)
    with nr_passkeys_col:
        st.metric(label='Registered Passkeys', value=nr_passkeys)


@st.fragment
def manage_users_view(
    df: pd.DataFrame,
    roles: Sequence[db.models.Role],
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
) -> None:
    r"""Manage the users of the application.

    The view allows to create, update and delete users.

    Parameters
    ----------
    df : pandas.DataFrame
        The selectable users to manage.

    roles: Sequence[streamlit_passwordless.db.models.Role]
        The roles of the users to use for filtering the selectable users.

    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.
    """

    filter_col, space_col, button_col, statistics_col = st.columns(
        [0.3, 0.1, 0.3, 0.3],
        vertical_alignment='bottom',
        gap='small',
    )
    with filter_col:
        left_col, right_col = st.columns([0.4, 0.6])
        with left_col:
            selected_user_state = user_state_radio_button()
        with right_col:
            selected_roles = user_role_multiselect(roles=roles)

    with space_col:
        pass

    with button_col:
        left_col, right_col = st.columns(2)
        with left_col:
            refresh_users_button(db_session=db_session)
        with right_col:
            create_user_button(db_session=db_session)

    with statistics_col:
        statistics_view(nr_users_database=df.shape[0], nr_users_bwp=0, nr_passkeys=0)

    if df.shape[0] > 0:
        df = filter_selectable_users(
            df=df, disabled=selected_user_state, roles={r.role_id for r in selected_roles}
        )
    selected_user_id = user_selectbox(df=df)

    st.divider()  # User and email

    if selected_user_id:
        db_user = db.get_user_by_user_id(session=db_session, user_id=selected_user_id)
    else:
        db_user = None

    left_col, right_col = st.columns([0.5, 0.5], vertical_alignment='top')
    with left_col:
        title_col, delete_button_col = st.columns([0.7, 0.3], vertical_alignment='bottom')
        with title_col:
            st.markdown('### Update User')
        with delete_button_col:
            delete_user_button(client=client, db_session=db_session, disabled=db_user is None)

        if selected_user_id is None:
            emails = []
            display_banner_message(
                message='Select a user to update!', message_type=BannerMessageType.INFO
            )
        elif db_user is None:
            emails = []
            display_banner_message(
                message='Selected user not found in database!',
                message_type=BannerMessageType.ERROR,
            )
        else:
            st.write(db_user)
            emails = db_user.emails

    with right_col:
        st.metric(label='Emails', value=len(emails))
        st.write(emails)

    st.divider()  # Passkeys

    left_col, right_col = st.columns([0.5, 0.5], vertical_alignment='top')
    with left_col:
        bitwarden_register_form_existing_user(
            client=client, db_session=db_session, user=st.session_state['stp-user']
        )
    with right_col:
        st.metric(label='Passkeys', value=3)

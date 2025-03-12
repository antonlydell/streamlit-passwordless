r"""The views of the admin page."""

# Third party
import streamlit as st

# Local
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

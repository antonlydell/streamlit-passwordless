r"""The components of the Streamlit Passwordless multi-page demo app."""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

import streamlit_passwordless as stp


def _format_user_sign_in_timestamp(timestamp: datetime) -> str:
    r"""Display info about the signed in user."""

    target_tz = tz if (tz := st.context.timezone) else 'UTC'
    return timestamp.astimezone(tz=ZoneInfo(target_tz)).isoformat(sep=' ', timespec='seconds')


def _display_user_info(user: stp.User) -> None:
    r"""Display info about the signed in user."""

    if (sign_in := user.sign_in) is None:
        passkey_nickname = ''
        sign_in_timestamp = ''
    else:
        passkey_nickname = sign_in.credential_nickname
        sign_in_timestamp = _format_user_sign_in_timestamp(sign_in.sign_in_timestamp)

    user_info = f"""\
### User Info
- **Username :**     {user.username}
- **Displayname :**  {user.displayname}
- **Role :**         {user.role.name}
- **Email :**        {user.email}
- **Passkey :**      {passkey_nickname}
- **Signed in at :** {sign_in_timestamp}
"""

    st.markdown(user_info)


def sidebar(user: stp.User | None, authenticated: bool = False) -> None:
    r"""Render the sidebar of the app if the user is authenticated.

    Parameters
    ----------
    user : streamlit_passwordless.User or None
        The signed in user or None if a user has not signed in yet.

    authenticated : bool, default False
        True if the user is authenticated and False otherwise.
    """

    if not authenticated or user is None:
        return

    with st.sidebar:
        _display_user_info(user=user)
        st.divider()
        stp.sign_out_button()

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

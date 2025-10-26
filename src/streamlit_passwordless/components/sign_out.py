r"""Components related to the sign out process."""

# Third party
import streamlit as st

# Local
from streamlit_passwordless.auth import sign_out
from streamlit_passwordless.models import User

from .config import SK_USER
from .core import ButtonType
from .ids import KEY_SIGN_OUT_BUTTON


def sign_out_button(
    user: User | None = None,
    label: str = 'Sign out',
    icon: str | None = None,
    button_type: ButtonType = 'primary',
    help: str | None = None,
    use_container_width: bool = False,
) -> tuple[bool, User | None]:
    r"""Render the sign out button.

    If clicked the user is signed out from the application.
    The button is disabled if a user is not signed in.

    Parameters
    ----------
    user : streamlit_passwordless.User or None, default None
        The user to sign out. If None the user to sign out is loaded from the
        session state using key :attr:`streamlit_passwordless.SK_USER`.

    label : str, default 'Sign out'
        The label of the sign out button. GitHub-flavored Markdown is supported.

    icon : str or None, default None
        An optional icon to display next to the `label` of the button.
        See the `icon` parameter of :func:`streamlit.button` for more info.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    help : str or None, default None
        An optional help text to display when hovering over the button.

    use_container_width : bool, default False
        If True the button will take upp the full width of the parent container
        and if False it will be sized to fit the content of `label` and `icon`.

    Returns
    -------
    clicked : bool
        True if the button was clicked and False otherwise.

    user : streamlit_passwordless.User or None
        The signed out user. None is returned if a user has not signed in yet.
    """

    user = st.session_state.get(SK_USER) if user is None else user

    clicked = st.button(
        label=label,
        key=KEY_SIGN_OUT_BUTTON,
        type=button_type,
        icon=icon,
        help=help,
        use_container_width=use_container_width,
        disabled=True if user is None else not user.is_authenticated,
        on_click=sign_out,
        kwargs={'user': user},
    )

    return clicked, user

r"""Functionality to check if a user is authorized to access content within an application."""

# Standard library
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

# Third party
import streamlit as st
from streamlit.navigation.page import StreamlitPage

# Local
from streamlit_passwordless.components.config import SK_USER, SK_USER_SIGN_IN
from streamlit_passwordless.models import Role, User

P = ParamSpec('P')
R = TypeVar('R')


def authorized(
    user: User | None = None, role: Role | None = None, redirect: str | StreamlitPage | None = None
) -> Callable[[Callable[P, R | None]], Callable[P, R | None]]:
    r"""A decorator to check if a user is authorized to access content of specified `role`.

    If `user` is authorized the decorated function is executed and if not a redirect to
    another page is possible.

    Parameters
    ----------
    user : User or None, default None
        The user to authorize. If None the user to authorize is loaded from the
        session state using key :attr:`streamlit_passwordless.SK_USER`.

    role : streamlit_passwordless.Role or int or None, default None
        The role to authorize `user` against. If the rank of the role of `user` is
        greater than or equal to the rank of `role` the `user` is authorized. If an
        integer is supplied it is assumed to be the rank of the role to authorize the
        user against. If None (the default) the user is authorized regardless of its role.
        The user must always be authenticated to be authorized.

    redirect : str or streamlit.navigation.page.StreamlitPage or None, default None
        The Streamlit page to redirect `user` to if not authorized. If str it should be
        the path, relative to the file passed to the ``streamlit run`` command, to the
        Python file containing the page to redirect to. See :func:`streamlit.switch_page`
        for more info. If None, and `user` is not authorized, no redirect is performed and
        the decorated function is simply not executed.
    """

    def decorator(func: Callable[P, R | None]) -> Callable[P, R | None]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            r"""Check if the user is authorized."""

            nonlocal user
            user = st.session_state.get(SK_USER) if user is None else user

            if user is None or not user.is_authorized(role=role):
                if redirect is None:
                    return None
                st.switch_page(redirect)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def sign_out(user: User | None) -> None:
    r"""Sign out a signed in user.

    Parameters
    ----------
    user : User or None, default None
        The user to sign out. If None the user to sign out is loaded from the
        session state using key :attr:`streamlit_passwordless.SK_USER`.
    """

    user = st.session_state.get(SK_USER) if user is None else user

    if user is not None:
        user.sign_in = None

    st.session_state[SK_USER_SIGN_IN] = None

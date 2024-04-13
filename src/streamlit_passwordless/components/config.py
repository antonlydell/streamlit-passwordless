r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local


# =====================================================================================
# Session state keys
# =====================================================================================

SK_BP_REGISTER_FROM_IS_VALID = 'bp-register-from-is-valid'
SK_BP_REGISTER_USER_RESULT = 'sk-bp-register-user-result'
SK_BP_USER_TO_REGISTER = 'sk-bp-user-to-register'


# =====================================================================================
# Icons
# =====================================================================================

ICON_ERROR = '🚨'
ICON_SUCCESS = '✅'
ICON_WARNING = '⚠️'


# =====================================================================================
# Functions
# =====================================================================================


def init_session_state() -> None:
    r"""Initialize the session state.

    Session state keys
    ------------------
    SK_BP_REGISTER_FROM_IS_VALID : bool, default False
        True if the Bitwarden Passwordless register form validation is
        valid and False otherwise.

    SK_BP_USER_TO_REGISTER : models.User | None, default None
        The user register.

    SK_BP_REGISTER_USER_RESULT : tuple[str, dict] | None, default None
        The result from the user registration.
    """

    none_keys = (SK_BP_USER_TO_REGISTER, SK_BP_REGISTER_USER_RESULT)
    for key in none_keys:
        st.session_state[key] = None

    st.session_state[SK_BP_REGISTER_FROM_IS_VALID] = False

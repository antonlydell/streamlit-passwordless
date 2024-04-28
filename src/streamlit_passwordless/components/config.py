r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local


# =====================================================================================
# Session state keys
# =====================================================================================

SK_BP_REGISTER_FROM_IS_VALID = 'bp-register-from-is-valid'
SK_BP_REGISTER_USER_RESULT = 'bp-register-user-result'
SK_BP_USER_TO_REGISTER = 'bp-user-to-register'
SK_BP_SIGN_IN_USER_RESULT = 'bp-sign-in-user-result'
SK_BP_VERIFIED_USER = 'bp-verified-user'


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

    SK_BP_SIGN_IN_USER_RESULT : tuple[str, dict] | None, default None
        The result from the user sign in process in the web browser.

    SK_BP_VERIFIED_USER : streamlit_passwordless.BitwardenPasswordlessVerifiedUser | None, default None
        A verified user from Bitwarden Passwordless.
    """

    none_keys = (
        SK_BP_USER_TO_REGISTER,
        SK_BP_REGISTER_USER_RESULT,
        SK_BP_SIGN_IN_USER_RESULT,
        SK_BP_VERIFIED_USER,
    )
    for key in none_keys:
        st.session_state[key] = None

    st.session_state[SK_BP_REGISTER_FROM_IS_VALID] = False

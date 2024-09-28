r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local


# =====================================================================================
# Session state keys
# =====================================================================================

SK_USER_SIGN_IN = 'stp-user-sign-in'
SK_DB_USER = 'stp-db-user'
SK_REGISTER_FORM_IS_VALID = 'stp-register-form-is-valid'

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
    SK_USER_SIGN_IN : streamlit_passwordless.UserSignIn or None, default None
        Details from Bitwarden Passwordless about the user that signed in.

    SK_DB_USER : streamlit_passwordless.db.models.User or None, default None
        The database user. If None the user does not exist in the database.

    SK_REGISTER_FORM_IS_VALID : bool, default False
        True if the input to register form is valid and False otherwise.
    """

    none_keys = (SK_USER_SIGN_IN, SK_DB_USER)
    for key in none_keys:
        st.session_state[key] = None

    st.session_state[SK_REGISTER_FORM_IS_VALID] = False

r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local


# =====================================================================================
# Session state keys
# =====================================================================================

SK_BP_VERIFIED_USER = 'stp-bp-verified-user'
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
    SK_BP_VERIFIED_USER : streamlit_passwordless.BitwardenPasswordlessVerifiedUser or None, default None
        A verified user from Bitwarden Passwordless.

    SK_DB_USER : streamlit_passwordless.db.models.User or None, default None
        The database user. If None the user does not exist in the database.

    SK_REGISTER_FORM_IS_VALID : bool, default False
        True if the input to register form is valid and False otherwise.
    """

    none_keys = (SK_BP_VERIFIED_USER, SK_DB_USER)
    for key in none_keys:
        st.session_state[key] = None

    st.session_state[SK_REGISTER_FORM_IS_VALID] = False

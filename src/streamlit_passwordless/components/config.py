r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local


# =====================================================================================
# Session state keys
# =====================================================================================

SK_USERNAME_IS_VALID = 'stp-username-is-valid'
SK_BP_VERIFIED_USER = 'stp-bp-verified-user'
SK_DB_USER = 'stp-db-user'


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
    SK_USERNAME_IS_VALID : bool, default False
        True if the input username from the user is valid, which allows the user
        to register a passkey credential. Assumed False until proven otherwise.

    SK_BP_VERIFIED_USER : streamlit_passwordless.BitwardenPasswordlessVerifiedUser or None, default None
        A verified user from Bitwarden Passwordless.

    SK_DB_USER : streamlit_passwordless.db.models.User or None, default None
        The database user. If None the user does not exist in the database.
    """

    none_keys = (SK_BP_VERIFIED_USER, SK_DB_USER)
    for key in none_keys:
        st.session_state[key] = None

    st.session_state[SK_USERNAME_IS_VALID] = False

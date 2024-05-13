r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local


# =====================================================================================
# Session state keys
# =====================================================================================

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
    SK_BP_VERIFIED_USER : streamlit_passwordless.BitwardenPasswordlessVerifiedUser | None, default None
        A verified user from Bitwarden Passwordless.
    """

    st.session_state[SK_BP_VERIFIED_USER] = None

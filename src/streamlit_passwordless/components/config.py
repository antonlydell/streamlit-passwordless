r"""Contains the Streamlit configuration of the web components."""

# Standard library

# Third party
import streamlit as st

# Local
from streamlit_passwordless.models import User

# =====================================================================================
# Session state keys
# =====================================================================================

SK_USER = 'stp-user'
SK_USER_SIGN_IN = 'stp-user-sign-in'
SK_DB_USER = 'stp-db-user'
SK_REGISTER_FORM_IS_VALID = 'stp-register-form-is-valid'
SK_REGISTER_FORM_VALIDATION_ERRORS = 'stp-register-form-validation-errors'
SK_ROLES = 'stp-roles'
SK_CUSTOM_ROLES = 'stp-custom-roles'
SK_SESSION_STATE_INITIALIZED = 'stp-session-state-initialized'
SK_CREATE_USER_FORM_IS_VALID = 'stp-create-user-form-is-valid'
SK_CREATE_USER_FORM_VALIDATION_ERRORS = 'stp-create-user-form-validation-errors'
SK_UPDATE_USER_FORM_IS_VALID = 'stp-update-user-form-is-valid'
SK_UPDATE_USER_FORM_VALIDATION_ERRORS = 'stp-update-user-form-validation-errors'

# =====================================================================================
# Icons
# =====================================================================================

ICON_ERROR = '🚨'
ICON_INFO = 'ℹ️'
ICON_SUCCESS = '✅'
ICON_WARNING = '⚠️'


# =====================================================================================
# Functions
# =====================================================================================


def init_session_state() -> None:
    r"""Initialize the session state.

    Session state keys
    ------------------
    SK_SESSION_STATE_INITIALIZED : bool
        If True the session state has been initialized
        and the function does not need to run again.

    SK_USER : streamlit_passwordless.User or None, default None
        The current user of the application. If None a user has not signed
        in or registered yet.

    SK_USER_SIGN_IN : streamlit_passwordless.UserSignIn or None, default None
        Details from Bitwarden Passwordless about the user that signed in.
        If None a user has not signed in yet.

    SK_DB_USER : streamlit_passwordless.db.models.User or None, default None
        The database object of the current user. If None the user does not exist or
        has not been loaded from the database.

    SK_REGISTER_FORM_IS_VALID : bool, default False
        True if the input to the register form is valid and False otherwise.

    SK_REGISTER_FORM_VALIDATION_ERRORS : dict[str, str]
        A dictionary mapping of the form field name to its error message
        for the register form.

    SK_ROLES : dict[str, streamlit_passwordless.Role]
        The available roles for a user.

    SK_CUSTOM_ROLES : dict[str, streamlit_passwordless.CustomRole]
        The available custom roles for a user.

    SK_CREATE_USER_FORM_IS_VALID : bool
        True if the input to the create user form is valid and False otherwise.

    SK_CREATE_USER_FORM_VALIDATION_ERRORS : dict[str, str]
        A dictionary mapping of the form field name to its error message
        for the create user form.
    """

    if st.session_state.get(SK_SESSION_STATE_INITIALIZED, False):
        return

    st.session_state[SK_SESSION_STATE_INITIALIZED] = True

    none_keys = (SK_USER, SK_USER_SIGN_IN, SK_DB_USER)
    for key in none_keys:
        st.session_state[key] = None

    false_keys = (SK_CREATE_USER_FORM_IS_VALID, SK_REGISTER_FORM_IS_VALID)
    for key in false_keys:
        st.session_state[key] = False

    empty_dict_keys = (
        SK_REGISTER_FORM_VALIDATION_ERRORS,
        SK_CREATE_USER_FORM_VALIDATION_ERRORS,
        SK_ROLES,
        SK_CUSTOM_ROLES,
    )
    for key in empty_dict_keys:
        st.session_state[key] = {}


def get_current_user() -> User | None:
    r"""Get the current user from the session state.

    Returns
    -------
    streamlit_passwordless.User or None
        The user from the session state. None is returned if a user has not signed in yet.
    """

    return st.session_state.get(SK_USER)

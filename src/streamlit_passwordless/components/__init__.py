r"""The components' library contains the web components of streamlit_passwordless."""

# Local
from .config import (
    ICON_ERROR,
    ICON_SUCCESS,
    ICON_WARNING,
    SK_CUSTOM_ROLES,
    SK_DB_USER,
    SK_REGISTER_FORM_IS_VALID,
    SK_ROLES,
    SK_SESSION_STATE_INITIALIZED,
    SK_USER,
    SK_USER_SIGN_IN,
    init_session_state,
)
from .register_form import bitwarden_register_form, bitwarden_register_form_existing_user
from .sign_in_form import bitwarden_sign_in_form

# The Public API
__all__ = [
    # config
    'ICON_ERROR',
    'ICON_SUCCESS',
    'ICON_WARNING',
    'SK_CUSTOM_ROLES',
    'SK_DB_USER',
    'SK_REGISTER_FORM_IS_VALID',
    'SK_ROLES',
    'SK_SESSION_STATE_INITIALIZED',
    'SK_USER',
    'SK_USER_SIGN_IN',
    'init_session_state',
    # register_form
    'bitwarden_register_form',
    'bitwarden_register_form_existing_user',
    # sign_in_form
    'bitwarden_sign_in_form',
]

r"""The components' library contains the web components of streamlit_passwordless."""

# Local
from .config import (
    ICON_ERROR,
    ICON_INFO,
    ICON_SUCCESS,
    ICON_WARNING,
    SK_CUSTOM_ROLES,
    SK_DB_USER,
    SK_REGISTER_FORM_IS_VALID,
    SK_ROLES,
    SK_SESSION_STATE_INITIALIZED,
    SK_USER,
    SK_USER_SIGN_IN,
    get_current_user,
    init_session_state,
)
from .core import (
    BannerContainer,
    BannerMessageType,
    Redirectable,
    display_banner_message,
    process_form_validation_errors,
)
from .create_user_form import create_user_form
from .register_form import bitwarden_register_form, bitwarden_register_form_existing_user
from .sign_in_form import bitwarden_sign_in_button, bitwarden_sign_in_form
from .sign_out import sign_out_button

# The Public API
__all__ = [
    # config
    'ICON_ERROR',
    'ICON_INFO',
    'ICON_SUCCESS',
    'ICON_WARNING',
    'SK_CUSTOM_ROLES',
    'SK_DB_USER',
    'SK_REGISTER_FORM_IS_VALID',
    'SK_ROLES',
    'SK_SESSION_STATE_INITIALIZED',
    'SK_USER',
    'SK_USER_SIGN_IN',
    'get_current_user',
    'init_session_state',
    # core
    'BannerContainer',
    'BannerMessageType',
    'Redirectable',
    'display_banner_message',
    'process_form_validation_errors',
    # create_user_form
    'create_user_form',
    # register_form
    'bitwarden_register_form',
    'bitwarden_register_form_existing_user',
    # sign_in_form
    'bitwarden_sign_in_button',
    'bitwarden_sign_in_form',
    # sign_out
    'sign_out_button',
]

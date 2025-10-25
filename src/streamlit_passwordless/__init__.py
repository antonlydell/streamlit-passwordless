r"""The streamlit-passwordless package.

streamlit-passwordless provides a user model for Streamlit applications based on the Bitwarden
passwordless technology. It allows users to securely authenticate with a Streamlit application
using the passkey FIDO2 and WebAuthn protocols.
"""

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app import admin_page, init_page, load_config, setup
from streamlit_passwordless.authorization import authorized, sign_out
from streamlit_passwordless.bitwarden_passwordless import (
    BITWARDEN_PASSWORDLESS_API_URL,
    BitwardenPasswordlessClient,
    BitwardenRegisterConfig,
    PasskeyCredential,
    create_bitwarden_passwordless_client,
    register_button,
    sign_in_button,
)
from streamlit_passwordless.components import (
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
    BannerContainer,
    BannerMessageType,
    Redirectable,
    bitwarden_register_form,
    bitwarden_register_form_existing_user,
    bitwarden_sign_in_button,
    bitwarden_sign_in_form,
    create_user_form,
    delete_user_button,
    display_banner_message,
    get_current_user,
    init_session_state,
    process_form_validation_errors,
    sign_out_button,
    update_user_form,
)
from streamlit_passwordless.config import (
    STP_BWP_PRIVATE_KEY,
    STP_BWP_PUBLIC_KEY,
    STP_BWP_URL,
    STP_DB_URL,
    STP_SECRETS_SECTION,
    ConfigManager,
)
from streamlit_passwordless.exceptions import (
    DatabaseCreateUserError,
    DatabaseError,
    DatabaseInvalidUrlError,
    DatabaseStatementError,
    RegisterUserError,
    SignInTokenVerificationError,
    StreamlitPasswordlessError,
)
from streamlit_passwordless.metadata import (
    __releasedate__,
    __version__,
    __versiontuple__,
)
from streamlit_passwordless.models import (
    AdminRole,
    CustomRole,
    Email,
    Role,
    SuperUserRole,
    User,
    UserID,
    UserRole,
    UserSignIn,
    ViewerRole,
)

# The Public API
__all__ = [
    # app
    'admin_page',
    'init_page',
    'load_config',
    'setup',
    # authorization
    'authorized',
    'sign_out',
    # bitwarden_passwordless
    'BITWARDEN_PASSWORDLESS_API_URL',
    'BitwardenPasswordlessClient',
    'BitwardenRegisterConfig',
    'create_bitwarden_passwordless_client',
    'PasskeyCredential',
    'register_button',
    'sign_in_button',
    # components
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
    'BannerContainer',
    'BannerMessageType',
    'Redirectable',
    'bitwarden_register_form',
    'bitwarden_register_form_existing_user',
    'bitwarden_sign_in_button',
    'bitwarden_sign_in_form',
    'create_user_form',
    'delete_user_button',
    'display_banner_message',
    'get_current_user',
    'init_session_state',
    'process_form_validation_errors',
    'sign_out_button',
    'update_user_form',
    # config
    'STP_BWP_PRIVATE_KEY',
    'STP_BWP_PUBLIC_KEY',
    'STP_BWP_URL',
    'STP_DB_URL',
    'STP_SECRETS_SECTION',
    'ConfigManager',
    # database
    'db',
    # exceptions
    'DatabaseError',
    'DatabaseCreateUserError',
    'DatabaseInvalidUrlError',
    'DatabaseStatementError',
    'RegisterUserError',
    'SignInTokenVerificationError',
    'StreamlitPasswordlessError',
    # metadata
    '__releasedate__',
    '__version__',
    '__versiontuple__',
    # models
    'AdminRole',
    'CustomRole',
    'Email',
    'Role',
    'SuperUserRole',
    'User',
    'UserID',
    'UserRole',
    'UserSignIn',
    'ViewerRole',
]

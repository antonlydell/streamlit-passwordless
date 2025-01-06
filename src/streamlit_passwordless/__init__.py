r"""The streamlit-passwordless package.

streamlit-passwordless provides a user model for Streamlit applications based on the Bitwarden
passwordless technology. It allows users to securely authenticate with a Streamlit application
using the passkey FIDO2 and WebAuthn protocols.
"""

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app import init_page, setup
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
    ICON_SUCCESS,
    ICON_WARNING,
    SK_CUSTOM_ROLES,
    SK_DB_USER,
    SK_REGISTER_FORM_IS_VALID,
    SK_ROLES,
    SK_SESSION_STATE_INITIALIZED,
    SK_USER,
    SK_USER_SIGN_IN,
    bitwarden_register_form,
    bitwarden_register_form_existing_user,
    bitwarden_sign_in_form,
    init_session_state,
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
from streamlit_passwordless.metadata import __releasedate__, __version__, __versiontuple__
from streamlit_passwordless.models import CustomRole, Email, Role, User, UserSignIn

# The Public API
__all__ = [
    # app
    'init_page',
    'setup',
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
    'ICON_SUCCESS',
    'ICON_WARNING',
    'SK_CUSTOM_ROLES',
    'SK_DB_USER',
    'SK_REGISTER_FORM_IS_VALID',
    'SK_ROLES',
    'SK_SESSION_STATE_INITIALIZED',
    'SK_USER',
    'SK_USER_SIGN_IN',
    'bitwarden_register_form',
    'bitwarden_register_form_existing_user',
    'bitwarden_sign_in_form',
    'init_session_state',
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
    'CustomRole',
    'Email',
    'Role',
    'User',
    'UserSignIn',
]

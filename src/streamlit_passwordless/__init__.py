r"""The streamlit-passwordless package.

streamlit-passwordless provides a user model for Streamlit applications based on the Bitwarden
passwordless technology. It allows users to securely authenticate with a Streamlit application
using the passkey FIDO2 and WebAuthn protocols.
"""

# Standard library
from datetime import date

# Local
import streamlit_passwordless.database as db
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
    bitwarden_register_form,
    bitwarden_register_form_existing_user,
    bitwarden_sign_in_form,
    init_session_state,
)
from streamlit_passwordless.components.config import (
    SK_DB_USER,
    SK_REGISTER_FORM_IS_VALID,
    SK_USER,
    SK_USER_SIGN_IN,
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
    DatabaseError,
    DatabaseInvalidUrlError,
    DatabaseStatementError,
    RegisterUserError,
    SignInTokenVerificationError,
    StreamlitPasswordlessError,
)
from streamlit_passwordless.models import CustomRole, Email, Role, User, UserRoleName, UserSignIn

__versiontuple__ = (0, 10, 0)
r"""The version of streamlit-passwordless in a comparable form.
Adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_
(MAJOR.MINOR.PATCH).
"""

__version__ = '0.10.0'
r"""The streamlit-passwordless version string."""

__releasedate__ = date(2024, 12, 18)
r"""The release date of the version specified in :data:`__versiontuple__`."""


# The Public API

__all__ = [
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
    'DatabaseInvalidUrlError',
    'DatabaseStatementError',
    'RegisterUserError',
    'SignInTokenVerificationError',
    'StreamlitPasswordlessError',
    # models
    'CustomRole',
    'Email',
    'Role',
    'User',
    'UserRoleName',
    'UserSignIn',
    # session state
    'SK_DB_USER',
    'SK_REGISTER_FORM_IS_VALID',
    'SK_USER',
    'SK_USER_SIGN_IN',
    # attributes
    '__versiontuple__',
    '__version__',
    '__releasedate__',
]

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
    BitwardenPasswordlessClient,
    BitwardenPasswordlessVerifiedUser,
    BitwardenRegisterConfig,
    PasskeyCredential,
    register_button,
    sign_in_button,
)
from streamlit_passwordless.components import (
    ICON_ERROR,
    ICON_SUCCESS,
    ICON_WARNING,
    bitwarden_register_form,
    bitwarden_sign_in_form,
    init_session_state,
)
from streamlit_passwordless.exceptions import (
    RegisterUserError,
    SignInTokenVerificationError,
    StreamlitPasswordlessError,
)

__versiontuple__ = (0, 6, 0)
r"""The version of streamlit-passwordless in a comparable form.
Adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_
(MAJOR.MINOR.PATCH).
"""

__version__ = '0.6.0'
r"""The streamlit-passwordless version string."""

__releasedate__ = date(2024, 8, 4)
r"""The release date of the version specified in :data:`__versiontuple__`."""


# The Public API

__all__ = [
    # bitwarden_passwordless
    'BitwardenPasswordlessClient',
    'BitwardenPasswordlessVerifiedUser',
    'BitwardenRegisterConfig',
    'PasskeyCredential',
    'register_button',
    'sign_in_button',
    # components
    'ICON_ERROR',
    'ICON_SUCCESS',
    'ICON_WARNING',
    'bitwarden_register_form',
    'bitwarden_sign_in_form',
    'init_session_state',
    # database
    'db',
    # exceptions
    'RegisterUserError,',
    'SignInTokenVerificationError',
    'StreamlitPasswordlessError',
    # attributes
    '__versiontuple__',
    '__version__',
    '__releasedate__',
]

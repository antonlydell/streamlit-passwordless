r"""The Bitwarden Passwordless package."""

# Local
from .backend import (
    BITWARDEN_PASSWORDLESS_API_URL,
    BitwardenPasswordlessClient,
    BitwardenRegisterConfig,
    PasskeyCredential,
)
from .cache import create_bitwarden_passwordless_client
from .frontend import FrontendError, FrontendResult, register_button, sign_in_button

# The Public API

__all__ = [
    'BITWARDEN_PASSWORDLESS_API_URL',
    'BitwardenPasswordlessClient',
    'BitwardenRegisterConfig',
    'create_bitwarden_passwordless_client',
    'FrontendError',
    'FrontendResult',
    'PasskeyCredential',
    'register_button',
    'sign_in_button',
]

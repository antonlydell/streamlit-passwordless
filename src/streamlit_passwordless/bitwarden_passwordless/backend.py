r"""The functions and models for interacting with the Bitwarden Passwordless backend API."""

# Standard library
from datetime import datetime, timedelta
from typing import Literal, TypeAlias

# Third party
from passwordless import (
    PasswordlessClient,
    PasswordlessClientBuilder,
    PasswordlessOptions,
)
from pydantic import Field

# Local
from streamlit_passwordless import common, exceptions, models


BackendClient: TypeAlias = PasswordlessClient


class BitwardenRegisterConfig(models.BaseModel):
    r"""The available passkey configuration when registering a new user.

    See the `Bitwarden Passwordless`_ documentation for more info about the parameters.

    .. _ Bitwarden Passwordless: https://docs.passwordless.dev/guide/api.html#register-token

    Parameters
    ----------
    attestation : Literal['none', 'direct', 'indirect'], default 'none'
        WebAuthn attestation conveyance preference. 'direct' and 'indirect' are exclusive to the
        Enterprise plan of Bitwarden Passwordless. Trial & Pro plans are limited to 'none'.

    authenticator_type : Literal['any', 'platform', 'cross-platform'], default 'any'
        WebAuthn authenticator attachment modality. 'platform' refers to platform specific options
        such as Windows Hello, FaceID or TouchID, while 'cross-platform' means roaming devices such
        as security keys. 'any' (default) means any authenticator type is allowed.

    discoverable : bool, default True
        True allows the user to sign in without a username or alias by creating a
        client-side discoverable credential.

    user_verification : Literal['preferred', 'required', 'discouraged'], default 'preferred'
        Set the preference for how user verification (e.g. PIN code or biometrics) works when
        authenticating.

    expires_at : datetime, default 'current datetime in UTC + 120 seconds'
        The timestamp in UTC when the registration token expires and becomes invalid.

    alias_hasing : bool, default True
        True means that aliases for a user are hashed before they are stored in the
        Bitwarden Passwordless database.
    """

    attestation: Literal['none', 'direct', 'indirect'] = 'none'
    authenticator_type: Literal['any', 'platform', 'cross-platform'] = 'any'
    discoverable: bool = True
    user_verification: Literal['preferred', 'required', 'discouraged'] = 'preferred'
    expires_at: datetime = Field(
        default_factory=lambda: common.get_current_datetime() + timedelta(seconds=120)
    )
    alias_hasing: bool = True


def _build_backend_client(private_key: str, url: str) -> BackendClient:
    r"""Build the Bitwarden Passwordless backend client.

    Parameters
    ----------
    private_key : str
        The private key that the client uses for authenticating with the
        Bitwarden Passwordless backend API.

    url : str
        The base url to the backend API.

    Returns
    -------
    BackendClient
        The backend client.
    """

    try:
        options = PasswordlessOptions(api_secret=private_key, api_url=url)
        return PasswordlessClientBuilder(options=options).build()
    except Exception as e:
        error_msg = f'Could not build Bitwarden backend client! {type(e).__name__} : {str(e)}'
        raise exceptions.StreamlitPasswordlessError(error_msg) from None

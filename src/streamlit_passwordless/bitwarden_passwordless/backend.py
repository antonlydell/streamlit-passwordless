r"""The functions and models for interacting with the Bitwarden Passwordless backend API."""

# Standard library
import logging
from datetime import datetime, timedelta
from typing import Literal, TypeAlias

# Third party
from passwordless import (
    PasswordlessClient,
    PasswordlessClientBuilder,
    PasswordlessError,
    PasswordlessOptions,
    RegisterToken,
)

# Local
from streamlit_passwordless import common, exceptions, models

BackendClient: TypeAlias = PasswordlessClient

logger = logging.getLogger(__name__)


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

    validity : timedelta, default timedelta(seconds=120)
        When the registration token expires and becomes invalid defined as an offset
        from the start of the registration process.

    alias_hashing : bool, default True
        True means that aliases for a user are hashed before they are stored in the
        Bitwarden Passwordless database.
    """

    attestation: Literal['none', 'direct', 'indirect'] = 'none'
    authenticator_type: Literal['any', 'platform', 'cross-platform'] = 'any'
    discoverable: bool = True
    user_verification: Literal['preferred', 'required', 'discouraged'] = 'preferred'
    validity: timedelta = timedelta(seconds=120)
    alias_hashing: bool = True

    @property
    def expires_at(self) -> datetime:
        r"""The expiry time of the registration token in timezone UTC."""

        return common.get_current_datetime() + self.validity


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


def _create_register_token(
    client: BackendClient, user: models.User, register_config: BitwardenRegisterConfig
) -> str:
    r"""Create a register token to use for registering a device for a user.

    Parameters
    ----------
    client : BackendClient
        The Bitwarden Passwordless backend client to use for creating the register token.

    user : streamlit_passwordless.models.User
        The user to register.

    register_config : BitwardenRegisterConfig
        The configuration for creating the register token.

    Returns
    -------
    str
        The token to use for registering a device for a user.

    Raises
    ------
    streamlit_passwordless.exceptions.RegisterUserError
        If an error occurs while trying to create the register token using the
        Bitwarden Passwordless backend API.
    """

    input_register_config = RegisterToken(
        user_id=user.user_id,
        username=user.username,
        display_name=user.displayname,
        attestation=register_config.attestation,
        authenticator_type=register_config.authenticator_type,
        discoverable=register_config.discoverable,
        user_verification=register_config.user_verification,
        aliases=user.aliases,
        alias_hashing=register_config.alias_hashing,
        expires_at=register_config.expires_at,
    )

    try:
        registered_token = client.register_token(register_token=input_register_config)
    except PasswordlessError as e:
        error_msg = f'Error creating register token! {str(e)}\nproblem_details: {e.problem_details}'
        data = {
            'input_register_config': input_register_config,
            'problem_details': e.problem_details,
        }
        logger.error(error_msg)
        raise exceptions.RegisterUserError(error_msg, data=data) from None
    else:
        logger.info(f'Successfully created register token for user_id={user.user_id}')

    return registered_token.token  # type: ignore

r"""The client to use for interacting with the Bitwarden Passwordless backend API."""

# Standard library
import logging
from datetime import datetime, timedelta
from typing import Any, Literal, TypeAlias

# Third party
from passwordless import (
    Credential,
    DeleteUser,
    PasswordlessClient,
    PasswordlessClientBuilder,
    PasswordlessError,
    PasswordlessOptions,
    RegisterToken,
    VerifySignIn,
)
from pydantic import AnyHttpUrl, Field, PrivateAttr

# Local
from streamlit_passwordless import common, exceptions, models

BackendClient: TypeAlias = PasswordlessClient
PasskeyCredential: TypeAlias = Credential

BITWARDEN_PASSWORDLESS_API_URL: AnyHttpUrl = AnyHttpUrl('https://v4.passwordless.dev')  # type: ignore

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


class BitwardenPasswordlessClient(models.BaseModel):
    r"""The client for interacting with Bitwarden Passwordless.

    Parameters
    ----------
    public_key : str
        The public key of the Bitwarden Passwordless application.

    private_key : str
        The private key of the Bitwarden Passwordless application.

    url : pydantic.AnyHttpUrl or str, default 'https://v4.passwordless.dev'
        The base url of the Bitwarden Passwordless application.

    register_config : streamlit_passwordless.BitwardenRegisterConfig
        The passkey configuration when registering a new user.
        If not specified the default configuration is used.
    """

    public_key: str
    private_key: str
    url: AnyHttpUrl = BITWARDEN_PASSWORDLESS_API_URL
    register_config: BitwardenRegisterConfig = Field(default_factory=BitwardenRegisterConfig)
    _backend_client: BackendClient = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        r"""Setup the Bitwarden Passwordless backend client."""

        try:
            options = PasswordlessOptions(api_secret=self.private_key, api_url=str(self.url))
            self._backend_client = PasswordlessClientBuilder(options=options).build()
        except PasswordlessError as e:
            error_msg = 'Could not build Bitwarden Passwordless backend client!'
            raise exceptions.StreamlitPasswordlessError(error_msg, e=e) from None

    def __hash__(self) -> int:
        return hash(self.private_key + self.public_key)

    def create_register_token(self, user: models.User, discoverable: bool | None = None) -> str:
        r"""Create a register token to use for registering a passkey with the user's device.

        Parameters
        ----------
        user : streamlit_passwordless.User
            The user to register.

        discoverable : bool or None, default None
            If True create a discoverable passkey and if False a non-discoverable passkey.
            If None the setting for discoverability from `self.register_config` is used.

        Returns
        -------
        str
            The register token.

        Raises
        ------
        streamlit_passwordless.RegisterUserError
            If an error occurs while trying to create the register token
            using the Bitwarden Passwordless backend API.
        """

        register_config = self.register_config
        input_register_token = RegisterToken(
            user_id=user.user_id,
            username=user.username,
            display_name=user.displayname,
            attestation=register_config.attestation,
            authenticator_type=register_config.authenticator_type,
            discoverable=register_config.discoverable if discoverable is None else discoverable,
            user_verification=register_config.user_verification,
            aliases=user.aliases,
            alias_hashing=register_config.alias_hashing,
            expires_at=register_config.expires_at,
        )

        try:
            registered_token = self._backend_client.register_token(
                register_token=input_register_token
            )
        except PasswordlessError as e:
            error_msg = f'Error creating register token! {str(e)}'
            data = {
                'input_register_config': input_register_token,
                'problem_details': e.problem_details,
            }
            raise exceptions.RegisterUserError(error_msg, data=data, e=e) from None

        return registered_token.token  # type: ignore

    def verify_sign_in(self, token: str) -> models.UserSignIn:
        r"""Verify the sign in token with the backend to complete the sign in process.

        Parameters
        ----------
        token : str
            The token to verify.

        Returns
        -------
        streamlit_passwordless.UserSignIn
            Details from Bitwarden Passwordless about the user that signed in.

        Raises
        ------
        streamlit_passwordless.SignInTokenVerificationError
            If the `token` token cannot be verified successfully.

        streamlit_passwordless.StreamlitPasswordlessError
            If an instance of `streamlit_passwordless.UserSignIn` cannot be
            successfully created.
        """

        try:
            verified_user = self._backend_client.sign_in(verify_sign_in=VerifySignIn(token=token))
        except PasswordlessError as e:
            error_msg = f'Error verifying the sign in token! {str(e)}'
            data = {'token': token, 'problem_details': e.problem_details}
            raise exceptions.SignInTokenVerificationError(error_msg, data=data, e=e) from None

        return models.UserSignIn.model_validate(verified_user)

    def get_credentials(self, user_id: str, origin: str | None = None) -> list[PasskeyCredential]:
        r"""Get the registered passkey credentials for a user.

        Parameters
        ----------
        user_id : str
            The unique ID of the user.

        origin : str or None, default None
            Filter the credentials by origin. Origin is the domain name a
            credential is registred to. If None all credentials are returned.

        Returns
        -------
        credentials : list[streamlit_passwordless.PasskeyCredential]
            The registered passkey credentials of the user.

        Raises
        ------
        streamlit_passwordless.StreamlitPasswordlessError
            If the credentials cannot be retrieved from Bitwarden Passwordless.
        """

        try:
            credentials: list[PasskeyCredential] = self._backend_client.get_credentials(
                user_id=user_id
            )
        except PasswordlessError as e:
            error_msg = f'Error retrieving credentials for {user_id=}!\nproblem_details: {e.problem_details}'
            data = {
                'user_id': user_id,
                'problem_details': e.problem_details,
            }
            raise exceptions.StreamlitPasswordlessError(error_msg, data=data) from None

        return [c for c in credentials if c.origin == origin] if origin else credentials

    def delete_user(self, user_id: str) -> None:
        r"""Delete a user from Bitwarden Passwordless.

        Parameters
        ----------
        user_id : str
            The unique ID of the user to delete.

        Raises
        ------
        streamlit_passwordless.StreamlitPasswordlessError
            If there is an error with deleting the user from Bitwarden Passwordless.
        """

        try:
            self._backend_client.delete_user(DeleteUser(user_id=user_id))
        except PasswordlessError as e:
            error_msg = f'Error deleting {user_id=}!\nproblem_details: {e.problem_details}'
            data = {
                'user_id': user_id,
                'problem_details': e.problem_details,
            }
            raise exceptions.StreamlitPasswordlessError(error_msg, data=data, e=e) from None

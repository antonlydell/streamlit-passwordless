r"""The client to use to interact with Bitwarden Passwordless."""

# Standard library
import logging
from typing import Any, TypeAlias

# Third party
from passwordless import (
    Credential,
    PasswordlessClient,
    PasswordlessClientBuilder,
    PasswordlessError,
    PasswordlessOptions,
)
from pydantic import AnyHttpUrl, Field, PrivateAttr

# Local
from streamlit_passwordless import exceptions, models

from . import backend

BackendClient: TypeAlias = PasswordlessClient
PasskeyCredential: TypeAlias = Credential
logger = logging.getLogger(__name__)


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
    url: AnyHttpUrl = AnyHttpUrl('https://v4.passwordless.dev')
    register_config: backend.BitwardenRegisterConfig = Field(
        default_factory=backend.BitwardenRegisterConfig
    )
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

    def create_register_token(self, user: models.User) -> str:
        r"""Create a register token to use for registering a passkey with the user's device.

        Parameters
        ----------
        user : streamlit_passwordless.User
            The user to register.

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

        return backend._create_register_token(
            client=self._backend_client,
            user=user,
            register_config=self.register_config,  # type: ignore
        )

    def verify_sign_in(self, token: str) -> backend.BitwardenPasswordlessVerifiedUser:
        r"""Verify the sign in token with the backend to complete the sign in process.

        Parameters
        ----------
        token : str
            The token to verify.

        Returns
        -------
        streamlit_passwordless.BitwardenPasswordlessVerifiedUser
            Details from Bitwarden Passwordless about the user that was signed in.

        Raises
        ------
        streamlit_passwordless.SignInTokenVerificationError
            If the `token` token cannot be verified successfully.

        streamlit_passwordless.StreamlitPasswordlessError
            If an instance of `backend.BitwardenPasswordlessVerifiedUser` cannot be
            successfully created.
        """

        return backend._verify_sign_in_token(client=self._backend_client, token=token)

    def get_credentials(self, user_id: str, origin: str | None = None) -> list[PasskeyCredential]:
        r"""Get the registered passkey credentials for a user.

        Parameters
        ----------
        client : BackendClient
            The Bitwarden Passwordless backend client to communicate
            with the Bitwarden Passwordless backend.

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

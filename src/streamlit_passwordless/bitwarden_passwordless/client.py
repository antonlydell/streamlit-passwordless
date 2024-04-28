r"""The client to use to interact with Bitwarden Passwordless."""

# Standard library
import logging
from typing import Any

# Third party
from pydantic import AnyHttpUrl, Field, PrivateAttr

# Local
from streamlit_passwordless import models

from . import backend, frontend

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
    _backend_client: backend.BackendClient = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        r"""Setup the Bitwarden Passwordless backend client."""

        self._backend_client = backend._build_backend_client(
            private_key=self.private_key, url=str(self.url)
        )

    def register_user(self, user: models.User, key: str = 'register_user') -> None:
        r"""Register a new user by creating and registring a passkey with the user's device.

        The result from the method is saved to the session state with a key defined by
        the `key` parameter. The type of the result is listed in the section `Returns`.

        Parameters
        ----------
        user : streamlit_passwordless.User
            The user to register.

        key : str, default 'register_user'
            The name of the session state key where the result from the method is saved.

        Returns
        -------
        token : str
            The public key of the created passkey, which the user will use for future sign-in
            operations. This key is saved to the Bitwarden Passwordless database.

        error : dict
            An error object containing information about if the registration process was
            successful or not.
        """

        register_token = backend._create_register_token(
            client=self._backend_client,
            user=user,
            register_config=self.register_config,  # type: ignore
        )
        frontend._register(
            register_token=register_token,
            public_key=self.public_key,
            credential_nickname=user.username,
            key=key,
        )

    def sign_in(
        self,
        alias: str | None = None,
        with_discoverable: bool = True,
        with_autofill: bool = False,
        key: str = 'sign_in',
    ) -> None:
        r"""Start the sign in process the web browser.

        The result from the method is saved to the session state with a key defined by
        the `key` parameter. The type of the result is listed in the section `Returns`.

        Parameters
        ----------
        alias : str or None, default None
            The alias of the user to sign in. If specified it will override the other sign in
            methods `with_discoverable`, and `with_autofill`.

        with_discoverable : bool, default True
            If True the browser's native UI prompt will be used to select the passkey to use for
            signing in. If False the sign in method is disabled. If True it will override the
            value of the `with_autofill` parameter. If `alias` is specified it will override this
            sign in method.

        with_autofill : bool, default False
            If True the browser's native autofill UI will be used to select the passkey to use for
            signing in. If False the sign in method is disabled. This method of signing in is
            overridden if `alias` is specified or `with_discoverable` is True.

        key : str, default 'sign_in'
            The name of the session state key where the result from the method is saved.

        Returns
        -------
        token : str
            The verification token to be used by the Bitwarden Passwordless backend to authenticate
            the sign in process.

        error : dict | None
            An error object containing information if there was an error with the sign in process.
        """

        frontend._sign_in(
            public_key=self.public_key,
            alias=alias,
            with_discoverable=with_discoverable,
            with_autofill=with_autofill,
            key=key,
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

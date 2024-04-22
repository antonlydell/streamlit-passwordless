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

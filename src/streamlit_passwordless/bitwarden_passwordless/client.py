r"""The client to use to interact with Bitwarden Passwordless."""

# Standard library
import logging

# Third party
from pydantic import AnyHttpUrl, validator

# Local
from streamlit_passwordless import exceptions, models

from . import backend, frontend

logger = logging.getLogger(__name__)


class BitwardenPasswordlessClient(models.BaseModel):
    r"""The client for interacting with Bitwarden Passwordless.

    Parameters
    ----------
    url : pydantic.AnyHttpUrl
        The base url of the Bitwarden Passwordless application.

    public_key : str
        The public key of the Bitwarden Passwordless application.

    private_key : str
        The private key of the Bitwarden Passwordless application.

    register_config : streamlit_passwordless.BitwardenRegisterConfig or None, default None
        The passkey configuration when registering a new user.
        If None the default configuration is used.
    """

    url: AnyHttpUrl
    public_key: str
    private_key: str
    register_config: backend.BitwardenRegisterConfig | None = None
    _backend_client: backend.BackendClient

    def __init__(
        self,
        url: str,
        public_key: str,
        private_key: str,
        register_config: backend.BitwardenRegisterConfig | None = None,
    ) -> None:
        r"""Setup the Bitwarden Passwordless backend client."""

        self._backend_client = backend._build_backend_client(private_key=private_key, url=url)
        super().__init__(
            url=url, public_key=public_key, private_key=private_key, register_config=register_config
        )

    @validator('register_config')
    def set_register_config_defaults(
        cls, register_config: backend.BitwardenRegisterConfig | None
    ) -> backend.BitwardenRegisterConfig:
        r"""Set the default value of the `register_config` attribute."""

        if register_config is None:
            return backend.BitwardenRegisterConfig()
        else:
            return register_config

    def register_user(self, user: models.User, key: str | None = None) -> str:
        r"""Register a new user by creating and registring a passkey with the user's device.

        Parameters
        ----------
        user : streamlit_passwordless.User
            The user to register.

        key : str or None, default None
            An optional key that uniquely identifies this component. If this is
            None, and the component's arguments are changed, the component will
            be re-mounted in the Streamlit frontend and lose its current state.

        Returns
        -------
        token : str
            The public key of the created passkey, which the user will use for future sign-in
            operations. This key is saved to the Bitwarden Passwordless database.

        Raises
        ------
        streamlit_passwordless.RegisterUserError
            If an error occurs while trying to register the user.
        """

        register_token = backend._create_register_token(
            client=self._backend_client,
            user=user,
            register_config=self.register_config,  # type: ignore
        )
        token, error = frontend._register(
            register_token=register_token,
            public_key=self.public_key,
            credential_nickname=user.username,
            key=key,
        )

        if token:
            return token
        else:
            error_msg = f'Error creating passkey for user ({user})! {error}'
            logger.error(error_msg)
            raise exceptions.RegisterUserError(error_msg, data=error)

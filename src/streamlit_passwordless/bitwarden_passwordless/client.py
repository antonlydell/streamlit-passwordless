r"""The client to use to interact with Bitwarden Passwordless."""

# Standard library

# Third party
from pydantic import AnyHttpUrl, validator

# Local
from streamlit_passwordless import models
from . import backend


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

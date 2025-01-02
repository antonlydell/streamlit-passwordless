r"""Functions for interacting with Bitwarden Passwordless that are cached by Streamlit."""

# Standard library
from datetime import timedelta

# Third party
import streamlit as st
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless.bitwarden_passwordless.backend import (
    BITWARDEN_PASSWORDLESS_API_URL,
    BitwardenPasswordlessClient,
    BitwardenRegisterConfig,
)


@st.cache_data(ttl=timedelta(days=7), show_spinner=False)
def create_bitwarden_passwordless_client(
    private_key: str,
    public_key: str,
    _url: AnyHttpUrl = BITWARDEN_PASSWORDLESS_API_URL,
    _register_config: BitwardenRegisterConfig | None = None,
) -> BitwardenPasswordlessClient:
    r"""Create the client to communicate with Bitwarden Passwordless.

    Parameters
    ----------
    public_key : str
        The public key of the Bitwarden Passwordless application.

    private_key : str
        The private key of the Bitwarden Passwordless application.

    _url : pydantic.AnyHttpUrl or str, default AnyHttpUrl('https://v4.passwordless.dev')
        The base url of the backend API of Bitwarden Passwordless. Specify this url
        if you are self-hosting Bitwarden Passwordless.

    _register_config : streamlit_passwordless.BitwardenRegisterConfig or None, default None
        The passkey configuration when registering a new user.
        If not specified the default configuration is used.

    Returns
    -------
    streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client.
    """

    return BitwardenPasswordlessClient(
        public_key=public_key,
        private_key=private_key,
        url=_url,
        register_config=BitwardenRegisterConfig() if _register_config is None else _register_config,
    )

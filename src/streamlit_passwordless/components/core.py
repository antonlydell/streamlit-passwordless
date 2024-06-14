r"""Helper functions and core components that can be used by other components."""

# Standard library
import logging

# Third party
import streamlit as st

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessVerifiedUser
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient

from . import config

logger = logging.getLogger(__name__)


def verify_sign_in(
    client: BitwardenPasswordlessClient, token: str
) -> tuple[BitwardenPasswordlessVerifiedUser | None, str]:
    r"""Verify the sign in token with the backend to complete the sign in process.

    Parameters
    ----------
    client : BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless API.

    token : str
        The token to verify.

    Returns
    -------
    verified_user : streamlit_passwordless.BitwardenPasswordlessVerifiedUser or None
        Details from Bitwarden Passwordless about the user that was signed in.
        None is returned if an error occurred during the sign in process. `verified_user` is
        also stored in the session state with the key `config.SK_BP_VERIFIED_USER`.

    error_msg : str
        An error message about what failed during the sign in process.
        An empty string is returned if no errors occurred.
    """

    error_msg = ''
    verified_user: BitwardenPasswordlessVerifiedUser | None = None

    try:
        verified_user = client.verify_sign_in(token=token)
    except exceptions.SignInTokenVerificationError as e:
        error_msg = str(e)
        logger.error(error_msg)
    except exceptions.StreamlitPasswordlessError as e:
        error_msg = f'Error creating verified user!\n{str(e)}'
        logger.error(error_msg)

    st.session_state[config.SK_BP_VERIFIED_USER] = verified_user

    return verified_user, error_msg

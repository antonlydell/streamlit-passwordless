r"""Helper functions and core components that can be used by other components."""

# Standard library
import logging
from typing import Literal, TypeAlias

# Third party
import streamlit as st

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient

from . import config

ButtonType: TypeAlias = Literal['primary', 'secondary']
logger = logging.getLogger(__name__)


def verify_sign_in(
    client: BitwardenPasswordlessClient, token: str
) -> tuple[models.UserSignIn | None, str]:
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
    user_sign_in : streamlit_passwordless.UserSignIn or None
        Details from Bitwarden Passwordless about the user that signed in.
        None is returned if an error occurred during the sign in process. `user_sign_in` is
        also stored in the session state with the key `config.SK_USER_SIGN_IN`.

    error_msg : str
        An error message about what failed during the sign in process.
        An empty string is returned if no errors occurred.
    """

    error_msg = ''
    user_sign_in: models.UserSignIn | None = None

    try:
        user_sign_in = client.verify_sign_in(token=token)
    except exceptions.SignInTokenVerificationError as e:
        error_msg = e.displayable_message
        logger.error(str(e))
    except exceptions.StreamlitPasswordlessError as e:
        error_msg = f'Error creating user sign in!\n{e.displayable_message}'
        logger.error(f'Error creating user sign in!\n{str(e)}')

    st.session_state[config.SK_USER_SIGN_IN] = user_sign_in

    return user_sign_in, error_msg

r"""Helper functions and core components that can be used by other components."""

# Standard library
import logging
from enum import StrEnum
from functools import partial
from typing import Literal, TypeAlias

# Third party
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessClient

from . import config

BannerContainer: TypeAlias = DeltaGenerator
ButtonType: TypeAlias = Literal['primary', 'secondary']
logger = logging.getLogger(__name__)


class BannerMessageType(StrEnum):
    r"""The banner message types defined in Streamlit Passwordless.

    Members
    -------
    INFO
        An info banner.

    SUCCESS
        A success banner.

    WARNING
        A warning banner.

    ERROR
        An error banner.
    """

    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'


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


def display_banner_message(
    message: str,
    message_type: BannerMessageType = BannerMessageType.SUCCESS,
    container: BannerContainer | None = None,
) -> None:
    r"""Display a message in a banner on a page.

    Parameters
    ----------
    message : str
        The message to display in the banner.

    message_type : BannerMessageType, default BannerMessageType.SUCCESS
        The type of message banner.

    container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which the banner will be displayed.
        Useful to make the banner appear at the desired location on a page. If None the banner
        will be displayed at the location of the page where the function is called.

    Raises
    ------
    streamlit_passwordless.StreamlitPasswordlessError
        If an invalid `message_type` is supplied.
    """

    banner_funcs = {
        BannerMessageType.INFO: partial(st.info, icon=config.ICON_INFO),
        BannerMessageType.SUCCESS: partial(st.success, icon=config.ICON_SUCCESS),
        BannerMessageType.WARNING: partial(st.warning, icon=config.ICON_WARNING),
        BannerMessageType.ERROR: partial(st.error, icon=config.ICON_ERROR),
    }
    func = banner_funcs.get(message_type)

    if func is None:
        valid_options = ', '.join(f'{v!r}' for v in BannerMessageType)
        error_msg = (
            f'Invalid value for display_banner_message({message_type=}). '
            f'Valid options are : {valid_options}'
        )
        logger.error(error_msg)
        raise exceptions.StreamlitPasswordlessError(message=error_msg, data=message_type)

    if container is None:
        func(message)
    else:
        with container:
            func(message)

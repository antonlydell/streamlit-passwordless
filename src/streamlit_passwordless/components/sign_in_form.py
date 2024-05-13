r"""The sign in form component."""

# Standard library
import logging
from typing import Literal

# Third party
import streamlit as st

from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import sign_in_button

# Local
from . import config, ids

logger = logging.getLogger(__name__)


def bitwarden_sign_in_form(
    client: BitwardenPasswordlessClient,
    with_alias: bool = True,
    with_discoverable: bool = True,
    with_autofill: bool = False,
    alias_field_label: str = 'Alias',
    alias_max_length: int = 50,
    alias_placeholder: str = 'syn.gates@ax7.com',
    title: str = '#### Sign in',
    border: bool = True,
    submit_button_label: str = 'Sign in',
    button_type: Literal['primary', 'secondary'] = 'primary',
) -> None:
    r"""Render the Bitwarden Passwordless sign in form.

    Allows the user to sign in to the application with a registered passkey.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless application.

    with_alias : bool, default True
        If True the field to enter the alias to use for signing in will be rendered. If False
        the field is not rendered and the other sign in methods `with_discoverable` or
        `with_autofill` should be used. If the user specifies an alias it will override the other
        sign in methods `with_discoverable` and `with_autofill`.

    with_discoverable : bool, default True
        If True the browser's native UI prompt will be used to select the passkey to use for
        signing in. If False the sign in method is disabled. If `alias` is specified it will
        override this sign in method.

    with_autofill : bool, default False
        If True the browser's native autofill UI will be used to select the passkey to use for
        signing in. If False the sign in method is disabled. This method of signing in is
        overridden if `alias` specified or `with_discoverable` is True.

    title : str, default '#### Sign in.'
        The title of the sign in from. Markdown is supported.

    alias_field_label: str, default 'Alias'
        The label of the alias field of the form.

    alias_max_length : int, default 50
        The maximum number of character allowed to be entered in to the alias field of the form.

    alias_placeholder : str, default 'syn.gates@ax7.com'
        The placeholder to use for the alias field of the form.

    border : bool, default True
        True if a border surrounding the form should be rendered and False
        to remove the border.

    submit_button_label : str, default 'Sign in'
        The label of the submit button.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the submit button.
    """

    error_msg = ''
    banner_container = st.empty()

    if with_alias is False and with_discoverable is False and with_autofill is False:
        with banner_container:
            error_msg = (
                f'At least one sign in method must be chosen!\n'
                f'*{with_alias=}*, *{with_discoverable=}*,  *{with_autofill=}*'
            )
            logger.error(error_msg)
            st.error(error_msg, icon=config.ICON_ERROR)
            return

    with st.container(border=border):
        st.markdown(title)
        if with_alias:
            st.text_input(
                label=alias_field_label,
                placeholder=alias_placeholder,
                max_chars=alias_max_length,
                help=(
                    'An alias of the user. If not supplied auto discover '
                    'of available credentials will be attempted.'
                ),
                key=ids.BP_SIGN_IN_FORM_ALIAS_TEXT_INPUT,
            )

        token, error, clicked = sign_in_button(
            public_key=client.public_key,
            alias=st.session_state.get(ids.BP_SIGN_IN_FORM_ALIAS_TEXT_INPUT),
            with_discoverable=with_discoverable,
            with_autofill=with_autofill,
            key=ids.BP_SIGN_IN_FORM_SUBMIT_BUTTON,
        )

    if not clicked:
        return

    if not token and error:
        error_msg = f'Error signing in!\nerror : {error}'
        logger.error(error_msg)
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    try:
        verified_user = client.verify_sign_in(token=token)
    except exceptions.SignInTokenVerificationError as e:
        error_msg = str(e)
        logger.error(error_msg)
    except exceptions.StreamlitPasswordlessError as e:
        error_msg = f'Error creating verified user!\n{str(e)}'
        logger.error(error_msg)

    if error_msg:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    st.session_state[config.SK_BP_VERIFIED_USER] = verified_user
    with banner_container:
        st.success(
            f'Successfully signed in user {verified_user.credential_nickname}',
            icon=config.ICON_SUCCESS,
        )

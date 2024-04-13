r"""The register-form component and its callback functions."""

# Standard library
import logging
from typing import Literal

# Third party
import streamlit as st

from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient

# Local
from . import config, ids

logger = logging.getLogger(__name__)


def _validate_form() -> None:
    r"""Validate the input to the registration form and create the user to register.

    The created user is saved to the session state with the key `config.SK_BP_USER_TO_REGISTER`.

    Session state
    -------------
    config.SK_BP_USER_TO_REGISTER : models.User | None
        The user to register. None is returned if a user
        could not be created from the form data.
    """

    error_msg = ''
    username = st.session_state[ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT]
    displayname = st.session_state[ids.BP_REGISTER_FORM_DISPLAYNAME_TEXT_INPUT]
    aliases = st.session_state[ids.BP_REGISTER_FORM_ALIASES_TEXT_INPUT]

    if not username:
        error_msg = 'The username field is required!'
        logger.error(error_msg)

    # Create a user
    if not error_msg:
        try:
            st.session_state[config.SK_BP_USER_TO_REGISTER] = models.User(
                username=username, displayname=displayname, aliases=aliases
            )
        except exceptions.StreamlitPasswordlessError as e:
            error_msg = str(e)
            logger.error(error_msg)

    if error_msg:
        st.error(error_msg, icon=config.ICON_ERROR)
        st.session_state[config.SK_BP_REGISTER_FROM_IS_VALID] = False
        st.session_state[config.SK_BP_USER_TO_REGISTER] = None
    else:
        st.session_state[config.SK_BP_REGISTER_FROM_IS_VALID] = True


def bitwarden_register_form(
    client: BitwardenPasswordlessClient,
    is_admin: bool = False,
    pre_authorized: bool = True,
    title: str = '#### Register a new passkey with your device.',
    clear_on_submit: bool = False,
    submit_button_label: str = 'Register',
    button_type: Literal['primary', 'secondary'] = 'primary',
) -> None:
    r"""Render the Bitwarden Passwordless register form.

    Allows the user to register an account with the application by creating
    and registrering a passkey with the user's device.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless application.

    is_admin : bool, default False
        True means that the user will be registered as an admin.

    pre_authorized : bool, default True
        If True require the username to exist in the pre_authorized table of the database
        to allow the user to register.

    title : str, default '#### Register a new passkey with your device.'
        The title of the registration from. Markdown is supported.

    clear_on_submit : bool, default False
        Clear the form when the submit button is pressed.

    submit_button_label : str, default 'Register'
        The label of the submit button.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the submit button.
    """

    banner_container = st.empty()

    with st.form(key=ids.BP_REGISTER_FORM, clear_on_submit=clear_on_submit):
        st.markdown(title)
        st.text_input(
            label='Username',
            placeholder='syn.gates@ax7.com',
            help='A unique identifier for the account. E.g. an email address.',
            key=ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT,
        )
        st.text_input(
            label='Displayname',
            placeholder='Synyster Gates',
            help='A descriptive name of the user.',
            key=ids.BP_REGISTER_FORM_DISPLAYNAME_TEXT_INPUT,
        )
        st.text_input(
            label='Alias',
            placeholder='syn;gates;afterlife',
            key=ids.BP_REGISTER_FORM_ALIASES_TEXT_INPUT,
            help=(
                'One or more aliases that can be used to sign in to the account. '
                'Aliases are separated by semicolon (";"). The username is always '
                'added as an alias.'
            ),
        )

        form_submit_button = st.form_submit_button(
            label=submit_button_label,
            type=button_type,
            on_click=_validate_form,
        )

    user = st.session_state[config.SK_BP_USER_TO_REGISTER]

    if form_submit_button and st.session_state[config.SK_BP_REGISTER_FROM_IS_VALID]:
        client.register_user(user=user, key=config.SK_BP_REGISTER_USER_RESULT)

    if (register_result := st.session_state[config.SK_BP_REGISTER_USER_RESULT]) is not None:
        _, error = register_result
        if error:
            error_msg = f'Error creating passkey for user ({user})!\nerror : {error}'
            logger.error(error_msg)
            with banner_container:
                st.error(error_msg, icon=config.ICON_ERROR)
            return
        else:
            msg = f'Successfully registered user: {user.username}!'
            logger.info(msg)
            with banner_container:
                st.success(msg, icon=config.ICON_SUCCESS)
        # Save user to database

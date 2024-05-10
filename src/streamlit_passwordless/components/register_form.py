r"""The register-form component and its callback functions."""

# Standard library
import logging
from typing import Literal

# Third party
import streamlit as st

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import register_button

from . import config, ids

logger = logging.getLogger(__name__)


def _validate_username() -> None:
    r"""Validate the input username."""

    username = st.session_state[ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT]
    if not username:
        error_msg = 'The username field is required!'
        logger.error(error_msg)
        st.error(error_msg, icon=config.ICON_ERROR)


def _create_user(
    username: str, displayname: str | None = None, aliases: str | None = None
) -> tuple[models.User | None, str]:
    r"""Create a new user to register.

    The created user is also saved to the session state
    with the key `config.SK_BP_USER_TO_REGISTER`.

    Parameters
    ----------
    username : str
        The username.

    displayname : str or None, default None
        The optional displayname of the user.

    aliases : str | None, default None
        The optional aliases of the user as a semicolon separated string.

    Returns
    -------
    user : models.User or None
        The user to create. None is returned if an error occurred while creating the user.

    error_msg : str
        The error message if a user could not be created successfully. If no errors an empty
        string is returned.
    """

    error_msg = ''
    try:
        user = models.User(username=username, displayname=displayname, aliases=aliases)
    except exceptions.StreamlitPasswordlessError as e:
        error_msg = str(e)
        logger.error(error_msg)
        user = None
    else:
        logger.debug(f'Successfully created user: {user}')

    st.session_state[config.SK_BP_USER_TO_REGISTER] = user
    return user, error_msg


def bitwarden_register_form(
    client: BitwardenPasswordlessClient,
    is_admin: bool = False,
    pre_authorized: bool = True,
    title: str = '#### Register a new passkey with your device.',
    submit_button_label: str = 'Register',
    border: bool = True,
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

    border : bool, default True
        If True a border will be rendered around the form.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the submit button.
    """

    user = None
    register_token = ''
    error_msg = ''
    banner_container = st.empty()

    with st.container(border=border):
        st.markdown(title)
        username = st.text_input(
            label='Username',
            placeholder='syn.gates@ax7.com',
            help='A unique identifier for the account. E.g. an email address.',
            on_change=_validate_username,
            key=ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT,
        )
        disabled = False if username else True
        displayname = st.text_input(
            label='Displayname',
            placeholder='Synyster Gates',
            help='A descriptive name of the user.',
            key=ids.BP_REGISTER_FORM_DISPLAYNAME_TEXT_INPUT,
            disabled=disabled,
        )
        aliases = st.text_input(
            label='Alias',
            placeholder='syn;gates;afterlife',
            key=ids.BP_REGISTER_FORM_ALIASES_TEXT_INPUT,
            disabled=disabled,
            help=(
                'One or more aliases that can be used to sign in to the account. '
                'Aliases are separated by semicolon (";"). The username is always '
                'added as an alias. An alias must be unique across all users.'
            ),
        )

        if username:
            user, error_msg = _create_user(
                username=username, displayname=displayname, aliases=aliases
            )
            if user is not None:
                try:
                    register_token = client.create_register_token(user=user)
                except exceptions.RegisterUserError as e:
                    error_msg = str(e)
                    logger.error(error_msg)

        token, error, clicked = register_button(
            register_token=register_token,
            public_key=client.public_key,
            credential_nickname=username,
            disabled=disabled,
            key=ids.BP_REGISTER_FORM_SUBMIT_BUTTON,
        )

    if disabled or not clicked:
        return

    if error_msg:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    if not token and error:
        error_msg = f'Error creating passkey for user ({user})!\nerror : {error}'
        logger.error(error_msg)
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    if token:
        msg = f'Successfully registered user: {user.username}!'
        logger.info(msg)
        with banner_container:
            st.success(msg, icon=config.ICON_SUCCESS)

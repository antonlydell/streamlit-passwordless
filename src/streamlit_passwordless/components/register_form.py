r"""The register-form component and its callback functions."""

# Standard library
import logging
from datetime import timedelta
from typing import Literal

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import register_button

from . import config, ids

logger = logging.getLogger(__name__)


def _validate_username(
    db_session: db.Session,
    is_authenticated: bool,
    pre_authorized: bool = False,
) -> bool:
    r"""Validate the input username.

    Updates the following session state keys:
    - `config.SK_DB_USER` :
        Assigns the database user object if one exists.

    Parameters
    ----------
    db_session : streamlit_passwordless.database.Session
        An active database session.

    is_authenticated : bool
        True if the user is authenticated. An authenticated user may create new credentials.

    pre_authorized : bool, default False
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.

    Returns
    -------
    bool
        True if the username is valid and False otherwise.
    """

    error_msg = ''
    username = st.session_state[ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT]

    if not username:
        error_msg = 'The username field is required!'
        logger.info(error_msg)
        st.error(error_msg, icon=config.ICON_ERROR)
        return

    user = db.get_user_by_username(session=db_session, username=username)
    credentials: list = []  # TODO:  Get passkey credentials of the user.

    if not user:
        st.session_state[config.SK_DB_USER] = None

        if pre_authorized:
            error_msg = (
                f'User {username} does not exist, but is required to exist '
                'to allow registration!'
            )
            logger.warning(error_msg)

    elif user:
        st.session_state[config.SK_DB_USER] = user

        if credentials and not is_authenticated:
            error_msg = (
                f'User {username} already exist! '
                'To add additional passkeys, please sign in first.'
            )
            logger.warning(error_msg)

    if error_msg:
        st.error(error_msg, icon=config.ICON_ERROR)
        return False
    else:
        return True


@st.cache_data
def _create_user(
    username: str,
    user_id: str | None = None,
    displayname: str | None = None,
    aliases: str | None = None,
) -> tuple[models.User | None, str]:
    r"""Create a new user to register.

    Parameters
    ----------
    username : str
        The username.

    user_id : str or None, default None
        The unique ID of the user, which serves as the primary key in the database.
        If None it will be generated as a uuid.

    displayname : str or None, default None
        The optional displayname of the user.

    aliases : str or None, default None
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
        user = models.User(
            username=username, user_id=user_id, displayname=displayname, aliases=aliases
        )
    except exceptions.StreamlitPasswordlessError as e:
        error_msg = str(e)
        logger.error(error_msg)
        user = None
    else:
        logger.debug(f'Successfully created user: {user}')

    return user, error_msg


@st.cache_data(
    ttl=timedelta(minutes=2),
    show_spinner=False,
    hash_funcs={BitwardenPasswordlessClient: hash, models.User: hash},
)
def _create_register_token(
    client: BitwardenPasswordlessClient, user: models.User
) -> tuple[str, str]:
    r"""Create a register token to register a new passkey with the user's device.

    Parameters
    ----------
    client : BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless API.

    user : models.User
        The user to register.

    Returns
    -------
    register_token : str
        The register token. An empty string is returned if an error occurred.

    error_msg : str
        An error message if the register token could not be created.
        An empty string is returned if no error occurred.
    """

    error_msg = ''

    try:
        register_token = client.create_register_token(user=user)
    except exceptions.RegisterUserError as e:
        error_msg = str(e)
        register_token = ''

    return register_token, error_msg


def _validate_form(
    db_session: db.Session, is_authenticated: bool, pre_authorized: bool = False
) -> None:
    r"""Validate the input fields of the register form.

    Parameters
    ----------
    db_session : streamlit_passwordless.database.Session
        An active database session.

    is_authenticated : bool
        True if the user is authenticated. An authenticated user may create new credentials.

    pre_authorized : bool, default False
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.
    """

    username_is_valid = _validate_username(
        db_session=db_session, is_authenticated=is_authenticated, pre_authorized=pre_authorized
    )
    st.session_state[config.SK_REGISTER_FORM_IS_VALID] = username_is_valid


def bitwarden_register_form(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    is_admin: bool = False,
    is_authenticated: bool = False,
    pre_authorized: bool = True,
    with_displayname: bool = False,
    with_alias: bool = False,
    title: str = '#### Register a new passkey with your device',
    border: bool = True,
    submit_button_label: str = 'Register',
    button_type: Literal['primary', 'secondary'] = 'primary',
    username_label: str = 'Username',
    username_max_length: int | None = 50,
    username_placeholder: str | None = 'john.doe@example.com',
    username_help: str | None = '__default__',
    displayname_label: str = 'Displayname',
    displayname_max_length: int | None = 50,
    displayname_placeholder: str | None = 'John Doe',
    displayname_help: str | None = '__default__',
    alias_label: str = 'Alias',
    alias_max_length: int | None = 50,
    alias_placeholder: str | None = 'j;john;jd',
    alias_help: str | None = '__default__',
) -> None:
    r"""Render the Bitwarden Passwordless register form.

    Allows the user to register an account with the application by creating
    and registrering a passkey with the user's device.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless application.

    db_session : streamlit_passwordless.db.Session
        An active database session.

    is_admin : bool, default False
        True means that the user will be registered as an admin.
        Not implemented yet.

    is_authenticated : bool, default False
        True if the user is authenticated. An authenticated user may create new credentials.

    pre_authorized : bool, default True
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.

    with_displayname : bool, default False
        If True the displayname field will be added to the form allowing
        the user to fill out a displayname for the account.

    with_alias : bool, default False
        If True the alias field will be added to the form allowing the user to fill
        out one or multiple aliases for the account. Aliases should be separated by
        by semicolon (";"). An alias must be unique across all users.

    title : str, default '#### Register a new passkey with your device'
        The title of the registration from. Markdown is supported.

    border : bool, default True
        If True a border will be rendered around the form.

    submit_button_label : str, default 'Register'
        The label of the submit button.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    Other Parameters
    ----------------
    username_label : str, default 'Username'
        The label of the username field.

    username_max_length : int or None, default 50
        The maximum allowed number of characters of the username field.
        If None the upper limit is removed.

    username_placeholder : str or None, default 'john.doe@example.com'
        The placeholder of the username field. If None the placeholder is removed.

    username_help : str or None, default '__default__'
        The help text to display for the username field. If '__default__' a sensible default
        help text will be used and if None the help text is removed.

    displayname_label : str, default 'Displayname'
        The label of the displayname field.

    displayname_max_length : int or None, default 50
        The maximum allowed number of characters of the displayname field.
        If None the upper limit is removed.

    displayname_placeholder : str or None, default 'John Doe'
        The placeholder of the displayname field. If None the placeholder is removed.

    displayname_help : str or None, default '__default__'
        The help text to display for the displayname field. If '__default__' a sensible default
        help text will be used and if None the help text is removed.

    alias_label : str, default 'Alias'
        The label of the alias field.

    alias_max_length : int or None, default 50
        The maximum allowed number of characters of the alias field.
        If None the upper limit is removed.

    alias_placeholder : str or None, default 'j;john;jd'
        The placeholder of the alias field. If None the placeholder is removed.

    alias_help : str or None, default '__default__'
        The help text to display for the alias field. If '__default__' a sensible default
        help text will be used and if None the help text is removed.
    """

    user = None
    register_token = ''
    error_msg = ''
    use_default_help = '__default__'
    _help: str | None = None
    banner_container = st.empty()

    with st.container(border=border):
        st.markdown(title)
        with st.form(key=ids.BP_REGISTER_FORM, clear_on_submit=False, border=False):
            if username_help == use_default_help:
                _help = 'A unique identifier for the account. E.g. an email address.'
            else:
                _help = username_help

            username = st.text_input(
                label=username_label,
                placeholder=username_placeholder,
                max_chars=username_max_length,
                help=_help,
                key=ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT,
            )
            if with_displayname:
                if displayname_help == use_default_help:
                    _help = 'A descriptive name of the user.'
                else:
                    _help = displayname_help

                displayname = st.text_input(
                    label=displayname_label,
                    placeholder=displayname_placeholder,
                    max_chars=displayname_max_length,
                    help=_help,
                    key=ids.BP_REGISTER_FORM_DISPLAYNAME_TEXT_INPUT,
                )
            else:
                displayname = None

            if with_alias:
                if alias_help == use_default_help:
                    _help = (
                        'One or more aliases that can be used to sign in to the account. '
                        'Aliases are separated by semicolon (";"). The username is always '
                        'added as an alias. An alias must be unique across all users.'
                    )
                else:
                    _help = alias_help

                aliases = st.text_input(
                    label=alias_label,
                    placeholder=alias_placeholder,
                    max_chars=alias_max_length,
                    help=_help,
                    key=ids.BP_REGISTER_FORM_ALIASES_TEXT_INPUT,
                )
            else:
                aliases = None

            st.form_submit_button(
                label='Validate',
                on_click=_validate_form,
                kwargs={
                    'db_session': db_session,
                    'pre_authorized': pre_authorized,
                    'is_authenticated': is_authenticated,
                },
            )

        db_user = st.session_state.get(config.SK_DB_USER)

        form_is_valid = st.session_state[config.SK_REGISTER_FORM_IS_VALID]
        disabled = not form_is_valid

        if form_is_valid:
            user, error_msg = _create_user(
                username=username,
                user_id=db_user.user_id if db_user else None,
                displayname=displayname,
                aliases=aliases,
            )
            if not error_msg:
                register_token, error_msg = _create_register_token(client=client, user=user)

        token, error, clicked = register_button(
            register_token=register_token,
            public_key=client.public_key,
            credential_nickname=username,
            disabled=disabled,
            label=submit_button_label,
            button_type=button_type,
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
    elif not token:
        error_msg = 'Unexpected error for missing token!'
        logger.error(error_msg)

    if error_msg:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    if not db_user:
        user_create = db.UserCreate(
            user_id=user.user_id, username=user.username, displayname=user.displayname
        )
        db_user = db.create_user(session=db_session, user=user_create)

    msg = f'Successfully registered user: {db_user.username}!'
    logger.info(msg)
    with banner_container:
        st.success(msg, icon=config.ICON_SUCCESS)

r"""The register-form component and its callback functions."""

# Standard library
import logging
from datetime import timedelta

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import register_button
from streamlit_passwordless.web import get_origin_header

from . import config, core, ids

logger = logging.getLogger(__name__)


USE_DEFAULT_HELP = '__default__'
CREDENTIAL_NICKNAME_HELP = (
    'A nickname for the passkey credential to make it easier to '
    'identify which device it belongs to.'
)


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
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
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
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        register_token = ''

    return register_token, error_msg


def _validate_form(
    db_session: db.Session,
    client: BitwardenPasswordlessClient,
    origin: str,
    pre_authorized: bool = False,
) -> None:
    r"""Validate the input fields of the register form.

    Updates the following session state keys:
    - `config.SK_DB_USER` :
        Assigns the database user object. None is assigned if the user does
        not exist in the database.

    - `config.SK_REGISTER_FORM_IS_VALID` :
        True if the form validation passed and False otherwise.

    Parameters
    ----------
    db_session : streamlit_passwordless.database.Session
        An active database session.

    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless backend API.

    origin : str
        The domain name of the application. Used to fetch existing passkey credentials of the
        the user for the application. An authenticated user with existing credentials to the
        application may create new credentials.

    pre_authorized : bool, default False
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.
    """

    error_msg = ''

    username = st.session_state[ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT]
    if not username:
        error_msg = 'The username field is required!'
        st.error(error_msg, icon=config.ICON_ERROR)
        st.session_state[config.SK_REGISTER_FORM_IS_VALID] = False
        return

    user = db.get_user_by_username(session=db_session, username=username)

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

        if origin:
            try:
                credentials = client.get_credentials(user_id=user.user_id, origin=origin)
            except exceptions.StreamlitPasswordlessError as e:
                error_msg = f'Could not get passkey credentials for user {username}!\n{str(e)}'
                credentials = []
        else:
            credentials = []

        if (user_sign_in := st.session_state.get(config.SK_USER_SIGN_IN)) is not None:
            is_authenticated = True if user_sign_in.user_id == user.user_id else False
        else:
            is_authenticated = False

        if not error_msg and credentials and not is_authenticated:
            error_msg = (
                f'User {username} already exist! '
                'To add additional passkeys, please sign in first.'
            )
            logger.warning(error_msg)

    if error_msg:
        st.error(error_msg, icon=config.ICON_ERROR)
        st.session_state[config.SK_REGISTER_FORM_IS_VALID] = False
    else:
        st.session_state[config.SK_REGISTER_FORM_IS_VALID] = True


def _create_user_in_database(session: db.Session, user: models.User) -> tuple[bool, str]:
    r"""Create a new user in the database.

    Parameters
    ----------
    session : streamlit_passwordless.db.Session
        An active database session.

    user : models.User
        The user to save to the database.

    Returns
    -------
    success : bool
        True if the user was successfully saved to the database and False otherwise.

    error_msg : str
        An error message to display to the user if there was an issue with creating the user
        in the database. If no error occurred an empty string is returned.
    """

    user_create = db.UserCreate(
        user_id=user.user_id, username=user.username, displayname=user.displayname
    )

    try:
        db.create_user(session=session, user=user_create, commit=True)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        success = False
    else:
        error_msg = ''
        success = True

    return success, error_msg


def _save_user_sign_in_to_database(
    session: db.Session, user_sign_in: models.UserSignIn
) -> tuple[bool, str]:
    r"""Save the user sign in entry to the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    user_sign_in : models.UserSignIn
        Data about the user sign in after registration.

    Returns
    -------
    success : bool
        True if the user sign in was successfully saved to the database and False otherwise.

    error_msg : str
        An error message to display to the user if there was an issue with saving the user sign
        in entry to the database. If no error occurred an empty string is returned.
    """

    user_sign_in_to_db = db.UserSignInCreate.model_validate(user_sign_in)

    try:
        db.create_user_sign_in(session=session, user_sign_in=user_sign_in_to_db, commit=True)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        success = False
    else:
        error_msg = ''
        success = True

    return success, error_msg


def bitwarden_register_form(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    is_admin: bool = False,
    pre_authorized: bool = False,
    with_displayname: bool = False,
    with_credential_nickname: bool = True,
    with_alias: bool = False,
    title: str = '#### Register a new passkey with your device',
    border: bool = True,
    validate_button_label: str = 'Validate',
    register_button_label: str = 'Register',
    validate_button_type: core.ButtonType | None = None,
    register_button_type: core.ButtonType = 'primary',
    clear_on_validate: bool = False,
    username_label: str = 'Username',
    username_max_length: int | None = 50,
    username_placeholder: str | None = 'john.doe@example.com',
    username_help: str | None = '__default__',
    displayname_label: str = 'Displayname',
    displayname_max_length: int | None = 50,
    displayname_placeholder: str | None = 'John Doe',
    displayname_help: str | None = '__default__',
    credential_nickname_label: str = 'Credential Nickname',
    credential_nickname_max_length: int | None = 50,
    credential_nickname_placeholder: str | None = 'Bitwarden or YubiKey-5C-NFC',
    credential_nickname_help: str | None = '__default__',
    alias_label: str = 'Alias',
    alias_max_length: int | None = 50,
    alias_placeholder: str | None = 'j;john;jd',
    alias_help: str | None = '__default__',
) -> models.User | None:
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

    pre_authorized : bool, default False
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.

    with_displayname : bool, default False
        If True the displayname field will be added to the form allowing
        the user to fill out a displayname for the account.

    with_credential_nickname : bool, default True
        If True the credential_nickname field will be added to the form allowing the user to
        specify a nickname for the passkey credential to create e.g. "YubiKey-5C-NFC".
        If False the username will be used as the `credential_nickname`.

    with_alias : bool, default False
        If True the alias field will be added to the form allowing the user to fill
        out one or multiple aliases for the account. Aliases should be separated by
        by semicolon (";"). An alias must be unique across all users.

    title : str, default '#### Register a new passkey with your device'
        The title of the registration from. Markdown is supported.

    border : bool, default True
        If True a border will be rendered around the form.

    validate_button_label : str, default 'Validate'
        The label of the validate button. The validate button validates the fields of the form.

    register_button_label : str, default 'Register'
        The label of the register button. The register button registers a new passkey with the
        user's device. It is enabled when the form is valid.

    validate_button_type : Literal['primary', 'secondary'] or None, default None
        The styling of the validate button. Emulates the `type` parameter of :func:`streamlit.button`.
        If None the button type will be 'secondary' when the form is valid and 'primary' when invalid.

    register_button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the register button. Emulates the `type` parameter of :func:`streamlit.button`.

    clear_on_validate : bool, default False
        True if the form fields should be cleared when the validate form button is clicked
        and False otherwise.

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

    credential_nickname_label : str, default 'Credential Nickname'
        The label of the credential_nickname field.

    credential_nickname_max_length : int or None, default 50
        The maximum allowed number of characters of the credential_nickname field.
        If None the upper limit is removed.

    credential_nickname_placeholder : str or None, default 'Bitwarden or YubiKey-5C-NFC'
        The placeholder of the credential_nickname field. If None the placeholder is removed.

    credential_nickname_help : str or None, default '__default__'
        The help text to display for the credential_nickname field. If '__default__' a sensible
        default help text is used and if None the help text is removed.

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

    Returns
    -------
    user : streamlit_passwordless.User or None
        The user object of the user that registered a passkey credential. None is returned if a user
        has not registered yet or if the registration failed and a user object could not be retrieved.
    """

    user = None
    error_msg = ''
    use_default_help = '__default__'
    _help: str | None = None
    banner_container = st.empty()

    with st.container(border=border):
        st.markdown(title)
        with st.form(key=ids.BP_REGISTER_FORM, clear_on_submit=clear_on_validate, border=False):
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

            if with_credential_nickname:
                credential_nickname = st.text_input(
                    label=credential_nickname_label,
                    placeholder=credential_nickname_placeholder,
                    max_chars=credential_nickname_max_length,
                    help=(
                        CREDENTIAL_NICKNAME_HELP
                        if credential_nickname_help == USE_DEFAULT_HELP
                        else credential_nickname_help
                    ),
                    key=ids.BP_REGISTER_FORM_CREDENTIAL_NICKNAME_TEXT_INPUT,
                )
            else:
                credential_nickname = username

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

            form_is_valid = st.session_state[config.SK_REGISTER_FORM_IS_VALID]
            if validate_button_type is None:
                button_type: core.ButtonType = 'secondary' if form_is_valid else 'primary'
            else:
                button_type = validate_button_type

            try:
                origin = get_origin_header()
            except exceptions.StreamlitPasswordlessError as e:
                logger.error(e.detailed_message)
                error_msg = e.displayable_message
                origin = ''

            st.form_submit_button(
                label=validate_button_label,
                type=button_type,
                on_click=_validate_form,
                kwargs={
                    'db_session': db_session,
                    'client': client,
                    'origin': origin,
                    'pre_authorized': pre_authorized,
                },
            )

        db_user = st.session_state.get(config.SK_DB_USER)

        disabled = not form_is_valid
        register_token = ''

        if form_is_valid:
            user, error_msg = _create_user(
                username=username,
                user_id=db_user.user_id if db_user else None,
                displayname=displayname,
                aliases=aliases,
            )
            if user is not None:
                register_token, error_msg = _create_register_token(client=client, user=user)

        token, error, clicked = register_button(
            register_token=register_token,
            public_key=client.public_key,
            credential_nickname=credential_nickname,
            disabled=disabled,
            label=register_button_label,
            button_type=register_button_type,
            key=ids.BP_REGISTER_FORM_SUBMIT_BUTTON,
        )

    if disabled or not clicked:
        return None

    if user is None:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return None

    if not token and error:
        error_msg = f'Error creating passkey for user ({username})!\nerror : {error}'
        logger.error(error_msg)
    elif not token:
        error_msg = 'Unexpected error for missing token!'
        logger.error(error_msg)

    if error_msg:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return None

    final_error_msg = ''
    if not db_user:
        can_save_sign_in_to_db, error_msg = _create_user_in_database(session=db_session, user=user)
        if not can_save_sign_in_to_db:
            final_error_msg = (
                f'Could not save user {user.username} to database! '
                'A mismatch between Bitwarden Passwordless.dev and local database has occurred!'
            )
    else:
        can_save_sign_in_to_db = True

    # The user is still registered even though the sign in may fail!
    user_sign_in, _ = core.verify_sign_in(client=client, token=token)
    user.sign_in = user_sign_in
    st.session_state[config.SK_USER] = user

    sign_in_failed_error_msg = (
        f'User {username} was registered, but the sign in attempt with registered passkey failed!'
    )
    if user_sign_in is None:
        final_error_msg = f'{final_error_msg}\n{sign_in_failed_error_msg}'
        save_user_sign_in_to_db_ok = False

    elif can_save_sign_in_to_db:
        if not user_sign_in.success:
            final_error_msg = f'{final_error_msg}\n{sign_in_failed_error_msg}'

        save_user_sign_in_to_db_ok, error_msg = _save_user_sign_in_to_database(
            session=db_session, user_sign_in=user_sign_in
        )
        if not save_user_sign_in_to_db_ok:
            final_error_msg = f'{final_error_msg}\n{error_msg}'
    else:
        save_user_sign_in_to_db_ok = False

    if not can_save_sign_in_to_db:
        with banner_container:
            logger.error(final_error_msg)
            st.error(final_error_msg, icon=config.ICON_ERROR)

    elif save_user_sign_in_to_db_ok:
        msg = f'Successfully registered user: {user.username}!'
        logger.info(msg)
        with banner_container:
            st.success(msg, icon=config.ICON_SUCCESS)

    elif not save_user_sign_in_to_db_ok:
        with banner_container:
            logger.warning(final_error_msg)
            st.warning(final_error_msg, icon=config.ICON_WARNING)

    else:
        pass

    return user

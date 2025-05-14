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
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import register_button
from streamlit_passwordless.web import get_origin_header

from . import config, core, ids

logger = logging.getLogger(__name__)


USE_DEFAULT_HELP = '__default__'

USERNAME_HELP = 'A unique identifier for the user.'

DISPLAYNAME_HELP = 'A descriptive name of the user.'

CREDENTIAL_NICKNAME_HELP = (
    'A nickname for the passkey credential to make it easier to '
    'identify which device it belongs to.'
)

DISCOVERABILITY_HELP = (
    'A discoverable passkey allows you to sign in without entering your username '
    'in contrast to a non-discoverable passkey. A non-discoverable does not consume '
    'a passkey slot on a YubiKey, which is the case for a discoverable passkey.'
)

ALIAS_HELP = (
    'One or more aliases that can be used to sign in to the account. '
    'Aliases are separated by semicolon (";"). The username is always '
    'added as an alias. An alias must be unique across all users.'
)


def _render_discoverability_component(
    label: str,
    component_type: Literal['toggle', 'radio'],
    default: bool,
    radio_button_option_names: tuple[str, str],
    radio_button_horizontal: bool,
    help_text: str | None,
    form_type: Literal['new_user', 'existing_user'],
    disabled: bool,
) -> bool:
    r"""Render the discoverability component for the register form.

    The component can be either a toggle switch or a radio button.

    Parameters
    ----------
    label : str
        The label of the discoverability component.

    component_type : Literal['toggle', 'radio']
        If the discoverability component should be rendered as a toggle switch or a radio button.

    default : bool
        The default option of the discoverability component. True means 'discoverable' and
        False 'non-discoverable'.

    radio_button_option_names : tuple[str, str]
        The option names of the radio button if `discoverability_component_type` is set to 'radio'.

    radio_button_horizontal : bool
       The radio button options are is rendered horizontally if True and vertically if False
       if `discoverability_component_type` is set to 'radio'.

    help_text : str or None
        The help text to display for the discoverability component. If '__default__'
        a sensible default help text is used and if None the help text is removed.

    form_type : Literal['new_user', 'existing_user']
        The form (`bitwarden_register_form`, `bitwarden_register_form_existing_user`) in which
        the component is rendered. Used for setting the ID:s of the toggle switch or radio button.
        This is important to avoid the error `streamlit.DuplicateWidgetID` if both
        `bitwarden_register_form` and `bitwarden_register_form_existing_user` are rendered on
        the same page in an application.

    disabled : bool
        True if the component should be disabled and False for enabled.

    Returns
    -------
    discoverable : bool
        The selected option for the discoverability, where True means 'discoverable'
        and False 'non-discoverable'.

    Raises
    ------
    exceptions.StreamlitPasswordlessError
        If invalid options for `component_type` or `form_type` are specified.
    """

    if form_type == 'new_user':
        toggle_switch_id = ids.BP_REGISTER_FORM_DISCOVERABILITY_TOGGLE_SWITCH
        radio_button_id = ids.BP_REGISTER_FORM_DISCOVERABILITY_RADIO_BUTTON
    elif form_type == 'existing_user':
        toggle_switch_id = ids.BP_REGISTER_FORM_EXISTING_USER_DISCOVERABILITY_TOGGLE_SWITCH
        radio_button_id = ids.BP_REGISTER_FORM_EXISTING_USER_DISCOVERABILITY_RADIO_BUTTON
    else:
        raise exceptions.StreamlitPasswordlessError(
            f"Invalid value for {form_type=}. Expected 'new_user' or 'existing_user'."
        )

    _help = DISCOVERABILITY_HELP if help_text == USE_DEFAULT_HELP else help_text
    if component_type == 'toggle':
        discoverable = st.toggle(
            label=label, value=default, help=_help, key=toggle_switch_id, disabled=disabled
        )
    elif component_type == 'radio':
        option_format_mapping = {
            True: radio_button_option_names[0],
            False: radio_button_option_names[1],
        }
        discoverable_radio = st.radio(  # May return none if index option is not specified.
            label=label,
            index=0 if default is True else 1,
            options=(True, False),
            format_func=lambda v: option_format_mapping[v],
            horizontal=radio_button_horizontal,
            help=_help,
            key=radio_button_id,
            disabled=disabled,
        )
        discoverable = True if discoverable_radio is None else discoverable_radio
    else:
        raise exceptions.StreamlitPasswordlessError(
            f"Invalid value for {component_type=}. Expected 'toggle' or 'radio'."
        )

    return discoverable


@st.cache_data(hash_funcs={models.Role: lambda r: r.name})
def _create_user(
    username: str,
    displayname: str | None = None,
    role: models.Role | None = None,
    email: str | None = None,
    aliases: str | None = None,
) -> models.User:
    r"""Create a new user to register.

    Parameters
    ----------
    username : str
        The username.

    displayname : str or None, default None
        The optional displayname of the user.

    role : models.Role or None, default None
        The role to assign to the user. If None the default role of
        :class:`streamlit_passwordless.User` is assigned.

    email : str or None, default None
        The optional email address to associate with the user.

    aliases : str or None, default None
        The optional aliases of the user as a semicolon separated string.

    Returns
    -------
    user : models.User
        The user to create.
    """

    user = models.User(
        username=username.strip(),
        displayname=None if displayname is None else displayname.strip(),
        role=models.UserRole if role is None else role,
        emails=[models.Email(email=email.strip().casefold(), rank=1)] if email else [],
        aliases=aliases,
    )
    logger.debug(f'Successfully created user: {user}')

    return user


@st.cache_data(
    ttl=timedelta(minutes=2),
    show_spinner=False,
    hash_funcs={BitwardenPasswordlessClient: hash, models.User: hash},
)
def _create_register_token(
    client: BitwardenPasswordlessClient, user: models.User, discoverable: bool | None = None
) -> tuple[str, str]:
    r"""Create a register token to register a new passkey with the user's device.

    Parameters
    ----------
    client : BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless API.

    user : models.User
        The user to register.

    discoverable : bool or None, default None
        If True create a discoverable passkey and if False a non-discoverable passkey.
        If None the setting for discoverability from `client.register_config` is used.

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
        register_token = client.create_register_token(user=user, discoverable=discoverable)
    except exceptions.RegisterUserError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        register_token = ''

    return register_token, error_msg


def _validate_username_field(
    db_session: db.Session, client: BitwardenPasswordlessClient, origin: str, pre_authorized: bool
) -> tuple[bool, bool]:
    r"""Validate the username text input field of the register form.

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

    pre_authorized : bool
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.

    Returns
    -------
    bool
        True if the username is valid for registration and False otherwise.

    bool
        True if the user that the supplied username is linked to is already authenticated
        and False otherwise.
    """

    validation_errors = st.session_state[config.SK_REGISTER_FORM_VALIDATION_ERRORS]
    validation_error_field = core.FormField.USERNAME
    username = st.session_state[ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT]

    if not username:
        validation_errors[validation_error_field] = 'The username field is required!'
        return False, False

    db_user, error_msg = core.get_user_from_database(
        session=db_session, username=username.strip().casefold()
    )
    st.session_state[config.SK_DB_USER] = db_user

    if db_user is None:
        if error_msg:  # DatabaseError
            validation_errors[validation_error_field] = error_msg
            return False, False
        elif not pre_authorized:
            return True, False

        error_msg = (
            f'User {username} does not exist, but is required to exist to allow registration!'
        )
        logger.warning(error_msg)
        validation_errors[validation_error_field] = error_msg
        return False, False

    if (user := config.get_current_user()) is None:
        is_authenticated = False
    else:
        is_authenticated = user.is_authenticated and db_user.user_id == user.user_id

    if is_authenticated:
        return True, True

    if origin:
        try:
            credentials = client.get_credentials(user_id=db_user.user_id, origin=origin)
        except exceptions.StreamlitPasswordlessError as e:
            error_msg = (
                f'Could not get passkey credentials for user {username}!\n{e.detailed_message}'
            )
            logger.error(error_msg)
            credentials = []

        if not credentials:
            return True, False

    error_msg = f'User {username} already exist! To add additional passkeys, please sign in first.'
    validation_errors[validation_error_field] = error_msg

    return False, False


def _validate_email_field(
    db_session: db.Session, email_is_username: bool, username: str | None
) -> bool:
    r"""Validate the email text input field of the register form.

    Parameters
    ----------
    db_session : streamlit_passwordless.database.Session
        An active database session.

    email_is_username : bool
        If True the username is the email address of the user and if False
        the username is distinct from an optional email address of the user.

    username : str or None
        The username of the user to create.

    Returns
    -------
    bool
        True if the email is valid for registration and False otherwise.
    """

    if email_is_username:
        email = username
        validation_error_field = core.FormField.USERNAME
    else:
        email = st.session_state.get(ids.BP_REGISTER_FORM_EMAIL_TEXT_INPUT)
        validation_error_field = core.FormField.EMAIL

    if email:
        validation_errors = st.session_state[config.SK_REGISTER_FORM_VALIDATION_ERRORS]
        db_email, error_msg = core.get_email_from_database(
            session=db_session, email=email.strip().casefold()
        )
        if error_msg:  # DatabaseError
            validation_errors[validation_error_field] = error_msg
            return False
        if db_email is not None:
            error_msg = f'{"User" if email_is_username else "Email"} {email} already exists!'
            validation_errors[validation_error_field] = error_msg
            return False

    return True


def _validate_form(
    db_session: db.Session,
    client: BitwardenPasswordlessClient,
    origin: str,
    pre_authorized: bool,
    email_is_username: bool,
    username: str,
) -> None:
    r"""Validate the input fields of the register form.

    Updates the following session state keys:
    - `streamlit_passwordless.SK_DB_USER` :
        Assigns the database user object. None is assigned if the user does
        not exist in the database.

    - `streamlit_passwordless.SK_REGISTER_FORM_IS_VALID` :
        True if the form validation passed and False otherwise.

    - `streamlit_passwordless.SK_REGISTER_FORM_VALIDATION_ERRORS` :
        A dictionary mapping of the user form field name to its error message.

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

    pre_authorized : bool
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.

    email_is_username : bool
        If True the username is the email address of the user and if False
        the username is distinct from an optional email address of the user.

    username : str
        The username of the user to create.
    """

    username_is_valid, is_authenticated = _validate_username_field(
        db_session=db_session, client=client, origin=origin, pre_authorized=pre_authorized
    )

    if is_authenticated:
        email_is_valid = True
    else:
        email_is_valid = _validate_email_field(
            db_session=db_session, email_is_username=email_is_username, username=username
        )
    st.session_state[config.SK_REGISTER_FORM_IS_VALID] = username_is_valid and email_is_valid


def bitwarden_register_form(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    role: models.Role | None = None,
    pre_authorized: bool = False,
    with_displayname: bool = False,
    with_email: bool = True,
    email_is_username: bool = False,
    with_credential_nickname: bool = True,
    with_discoverability: bool = False,
    with_alias: bool = False,
    title: str = '#### Register a new passkey with your device',
    border: bool = True,
    validate_button_label: str = 'Validate',
    register_button_label: str = 'Register',
    validate_button_type: core.ButtonType | None = None,
    register_button_type: core.ButtonType = 'primary',
    clear_on_validate: bool = False,
    banner_container: core.BannerContainer | None = None,
    redirect: core.Redirectable | None = None,
    created_by_user_id: str | None = None,
    username_label: str = 'Username',
    username_max_length: int | None = 50,
    username_placeholder: str | None = 'john.doe',
    username_help: str | None = '__default__',
    displayname_label: str = 'Displayname',
    displayname_max_length: int | None = 50,
    displayname_placeholder: str | None = 'John Doe',
    displayname_help: str | None = '__default__',
    email_label: str = 'Email',
    email_max_length: int | None = 50,
    email_placeholder: str | None = 'john.doe@example.com',
    email_help: str | None = 'An email address to associate with the user.',
    credential_nickname_label: str = 'Credential Nickname',
    credential_nickname_max_length: int | None = 50,
    credential_nickname_placeholder: str | None = 'Bitwarden or YubiKey-5C-NFC',
    credential_nickname_help: str | None = '__default__',
    discoverability_label: str = 'Discoverable Passkey',
    discoverability_component_type: Literal['toggle', 'radio'] = 'toggle',
    discoverability_default_option: bool = True,
    discoverability_radio_button_options: tuple[str, str] = ('Discoverable', 'Non-Discoverable'),
    discoverability_radio_button_horizontal: bool = True,
    discoverability_help: str | None = '__default__',
    alias_label: str = 'Alias',
    alias_max_length: int | None = 50,
    alias_placeholder: str | None = 'j;john;jd',
    alias_help: str | None = '__default__',
) -> tuple[models.User | None, bool]:
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

    role : streamlit_passwordless.Role or None, default None
        The role to assign to the user. If None the user will be assigned the default
        user role of :class:`streamlit_passwordless.User` i.e. a role with name
        :attr:`streamlit_passwordless.UserRoleName.USER`.

    pre_authorized : bool, default False
        If True require a user with the input username to exist in the database to allow
        the user to register a new passkey credential. If False omit this validation.

    with_displayname : bool, default False
        If True the displayname field will be added to the form allowing
        the user to fill out a displayname for the account.

    with_email : bool, default True
        If True the email field is added to the form to enable to
        enter an email address to associate with the user.

    email_is_username : bool, default False
        If True the username field will prompt to enter an email address, which will be used
        as the username and be added as an email address of the user.

    with_credential_nickname : bool, default True
        If True the credential_nickname field will be added to the form allowing the user to
        specify a nickname for the passkey credential to create e.g. "YubiKey-5C-NFC".
        If False the username will be used as the `credential_nickname`.

    with_discoverability : bool, default False
        If True the discoverability component is added to the form allowing the user to toggle
        between creating a *discoverable* or *non-discoverable* passkey. A discoverable passkey
        allows the user to sign in without entering the username in contrast to a non-discoverable
        passkey, which is traditionally used for a MFA setup. A discoverable passkey consumes a
        passkey slot on a YubiKey, while a non-discoverable does not. In most cases you want to
        create a discoverable passkey, which is also the default when the component is not enabled.
        The component can be rendered as a toggle switch (default) or a radio button by specifying
        the option `discoverability_component_type`.

    with_alias : bool, default False
        If True the alias field will be added to the form allowing the user to fill
        out one or multiple aliases for the account. Aliases should be separated by
        by semicolon (";"). An alias must be unique across all users.

    title : str, default '#### Register a new passkey with your device'
        The title of the registration form. Markdown is supported.

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

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the register user process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the form.

    redirect : str or streamlit.navigation.page.StreamlitPage or None, default None
        The Streamlit page to redirect `user` to on successful registration. If str it should
        be the path, relative to the file passed to the ``streamlit run`` command, to the
        Python file containing the page to redirect to. See :func:`streamlit.switch_page`
        for more info. If None no redirect is performed.

    created_by_user_id : str or None, default None
        The ID of the user that is creating the new user. If None the ID of
        the created user will be used if the user does not already exist.

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

    email_label : str, default 'Email'
        The label of the email field.

    email_max_length : int or None, default 50
        The maximum allowed number of characters of the email field.
        If None the upper limit is removed.

    email_placeholder : str or None, default 'john.doe@example.com'
        The placeholder of the email field. If None the placeholder is removed.

    email_help : str or None, default 'An email address to associate with the user.'
        The help text to display for the email field. If None the help text is removed.

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

    discoverability_label : str, default 'Discoverable Passkey'
        The label of the discoverability component.

    discoverability_component_type : Literal['toggle', 'radio'], default 'toggle'
        If the discoverability component should be rendered as a toggle switch or a radio button.

    discoverability_default_option : bool, default True
        The default option of the discoverability component. True means 'discoverable' and
        False 'non-discoverable'.

    discoverability_radio_button_options : tuple[str, str], default ('Discoverable', 'Non-Discoverable')
        The option names of the radio button if `discoverability_component_type` is set to 'radio'.

    discoverability_radio_button_horizontal : bool, default True
       The radio button options are rendered horizontally if True and vertically if False
       if `discoverability_component_type` is set to 'radio'.

    discoverability_help : str or None, default '__default__'
        The help text to display for the discoverability component. If '__default__' a sensible
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

    bool
        True if the created user has registered a passkey and False otherwise.
    """

    user = None
    error_msg = ''
    banner_container = st.empty() if banner_container is None else banner_container
    banner_container_mapping = {}

    with st.container(border=border):
        st.markdown(title)
        with st.form(key=ids.BP_REGISTER_FORM, clear_on_submit=clear_on_validate, border=False):
            if email_is_username:
                username_label = email_label
                username_placeholder = email_placeholder
                username_max_length = email_max_length

            username_error_banner = st.empty()
            banner_container_mapping[core.FormField.USERNAME] = username_error_banner

            username = st.text_input(
                label=username_label,
                placeholder=username_placeholder,
                max_chars=username_max_length,
                help=USERNAME_HELP if username_help == USE_DEFAULT_HELP else username_help,
                key=ids.BP_REGISTER_FORM_USERNAME_TEXT_INPUT,
            )

            if with_displayname:
                displayname = st.text_input(
                    label=displayname_label,
                    placeholder=displayname_placeholder,
                    max_chars=displayname_max_length,
                    help=(
                        DISPLAYNAME_HELP
                        if displayname_help == USE_DEFAULT_HELP
                        else displayname_help
                    ),
                    key=ids.BP_REGISTER_FORM_DISPLAYNAME_TEXT_INPUT,
                )
            else:
                displayname = None

            if with_email:
                if not email_is_username:
                    email_error_banner = st.empty()
                    banner_container_mapping[core.FormField.EMAIL] = email_error_banner
                    email = st.text_input(
                        label=email_label,
                        placeholder=email_placeholder,
                        max_chars=email_max_length,
                        help=email_help,
                        key=ids.BP_REGISTER_FORM_EMAIL_TEXT_INPUT,
                    )
                else:
                    email = username
            else:
                email = None

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

            if with_discoverability:
                discoverable = _render_discoverability_component(
                    label=discoverability_label,
                    component_type=discoverability_component_type,
                    default=discoverability_default_option,
                    radio_button_option_names=discoverability_radio_button_options,
                    radio_button_horizontal=discoverability_radio_button_horizontal,
                    help_text=discoverability_help,
                    form_type='new_user',
                    disabled=False,
                )
            else:
                discoverable = None

            if with_alias:
                aliases = st.text_input(
                    label=alias_label,
                    placeholder=alias_placeholder,
                    max_chars=alias_max_length,
                    help=ALIAS_HELP if alias_help == USE_DEFAULT_HELP else alias_help,
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
                    'email_is_username': email_is_username,
                    'username': username,
                },
            )

        db_user = st.session_state.get(config.SK_DB_USER)
        register_token = ''

        if form_is_valid:
            if db_user:
                user = models.User.model_validate(db_user)
            else:
                user = _create_user(
                    username=username,
                    displayname=displayname,
                    role=role,
                    email=email,
                    aliases=aliases,
                )
            register_token, error_msg = _create_register_token(
                client=client, user=user, discoverable=discoverable
            )

        form_is_not_valid = not form_is_valid

        token, error, clicked = register_button(
            register_token=register_token,
            public_key=client.public_key,
            credential_nickname=credential_nickname.strip(),
            disabled=form_is_not_valid,
            label=register_button_label,
            button_type=register_button_type,
            key=ids.BP_REGISTER_FORM_SUBMIT_BUTTON,
        )

    if form_is_not_valid:
        validation_error_key = config.SK_REGISTER_FORM_VALIDATION_ERRORS
        core.process_form_validation_errors(
            validation_errors=st.session_state[validation_error_key],
            banner_container_mapping=banner_container_mapping,  # type: ignore
            default_banner_container=banner_container,
        )
        st.session_state[validation_error_key] = {}

        return user, False

    if not clicked:
        return user, False

    if user is None:
        core.display_banner_message(
            message=error_msg, message_type=core.BannerMessageType.ERROR, container=banner_container
        )
        return user, False

    if not token:
        if error:
            error_msg = f'Error creating passkey for user "{username}"!\nerror : {error}'
        else:
            error_msg = 'Unexpected error for missing register token!'

        logger.error(error_msg)
        core.display_banner_message(
            message=error_msg, message_type=core.BannerMessageType.ERROR, container=banner_container
        )
        return user, False

    final_error_msg = ''
    if not db_user:
        can_save_sign_in_to_db, error_msg = core.create_user_in_database(
            session=db_session,
            user=user,
            created_by_user_id=created_by_user_id if created_by_user_id else user.user_id,
        )
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
        f'User {username} was registered, but the sign in attempt '
        f'with registered passkey "{credential_nickname}" failed!'
    )
    if user_sign_in is None:
        final_error_msg = f'{final_error_msg}\n{sign_in_failed_error_msg}'
        save_user_sign_in_to_db_ok = False

    elif can_save_sign_in_to_db:
        if not user_sign_in.success:
            final_error_msg = f'{final_error_msg}\n{sign_in_failed_error_msg}'

        save_user_sign_in_to_db_ok, error_msg = core.save_user_sign_in_to_database(
            session=db_session, user_sign_in=user_sign_in
        )
        if not save_user_sign_in_to_db_ok:
            final_error_msg = f'{final_error_msg}\n{error_msg}'
    else:
        save_user_sign_in_to_db_ok = False

    if not can_save_sign_in_to_db:
        logger.error(final_error_msg)
        core.display_banner_message(
            message=final_error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )

    elif save_user_sign_in_to_db_ok:
        msg = f'Successfully registered user: {user.username}!'
        logger.info(msg)
        core.display_banner_message(
            message=msg, message_type=core.BannerMessageType.SUCCESS, container=banner_container
        )
        if redirect:
            st.switch_page(redirect)

    elif not save_user_sign_in_to_db_ok:
        logger.warning(final_error_msg)
        core.display_banner_message(
            message=final_error_msg,
            message_type=core.BannerMessageType.WARNING,
            container=banner_container,
        )

    else:
        pass

    return user, True


def bitwarden_register_form_existing_user(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    user: models.User | db.models.User | None = None,
    get_current_user: bool = True,
    with_credential_nickname: bool = True,
    with_discoverability: bool = False,
    title: str = '#### Register a new passkey with your device',
    border: bool = True,
    register_button_label: str = 'Register',
    register_button_type: core.ButtonType = 'primary',
    banner_container: core.BannerContainer | None = None,
    redirect: core.Redirectable | None = None,
    credential_nickname_label: str = 'Credential Nickname',
    credential_nickname_max_length: int | None = 50,
    credential_nickname_placeholder: str | None = 'Bitwarden or YubiKey-5C-NFC',
    credential_nickname_help: str | None = '__default__',
    discoverability_label: str = 'Discoverable Passkey',
    discoverability_component_type: Literal['toggle', 'radio'] = 'toggle',
    discoverability_default_option: bool = True,
    discoverability_radio_button_options: tuple[str, str] = ('Discoverable', 'Non-Discoverable'),
    discoverability_radio_button_horizontal: bool = True,
    discoverability_help: str | None = '__default__',
) -> tuple[models.User | None, bool]:
    r"""Render the Bitwarden Passwordless register form for an existing user.

    Allows an existing user to register a new passkey credential with the application.
    The register button is disabled if the user is not signed in.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless backend API.

    db_session : streamlit_passwordless.db.Session
        An active database session.

    user : streamlit_passwordless.User or streamlit_passwordless.db.User or None, default None
        The user for which to register a passkey credential. If None the user from the session
        state `streamlit_passwordless.SK_USER` is used (if `get_current_user` is True). If `user`
        is not signed in the register button is disabled. `user.sign_in` is modified with the sign
        in entry with the newly registered passkey after it has been created. The session state
        :attr:`streamlit_passwordless.SK_USER` is updated with the modified `user`. An instance of
        :class:`streamlit_passwordless.db.User` should be supplied for the use case when an admin
        needs to register a passkey for a selected user.

    get_current_user : bool, default True
        If True the current user will be retrieved from the session state if `user` is None.
        If set to False it will ensure that the form is disabled if `user` is None.

    with_credential_nickname : bool, default True
        If True the credential_nickname field will be added to the form allowing the user to
        specify a nickname for the passkey credential to create e.g. "YubiKey-5C-NFC".
        If False the username will be used as the `credential_nickname`.

    with_discoverability : bool, default False
        If True the discoverability component is added to the form allowing the user to toggle
        between creating a *discoverable* or *non-discoverable* passkey. A discoverable passkey
        allows the user to sign in without entering the username in contrast to a non-discoverable
        passkey, which is traditionally used for a MFA setup. A discoverable passkey consumes a
        passkey slot on a YubiKey, while a non-discoverable does not. In most cases you want to
        create a discoverable passkey, which is also the default when the component is not enabled.
        The component can be rendered as a toggle switch (default) or a radio button by specifying
        the option `discoverability_component_type`.

    title : str, default '#### Register a new passkey with your device'
        The title of the registration form. Markdown is supported.

    border : bool, default True
        If True a border will be rendered around the form.

    register_button_label : str, default 'Register'
        The label of the register button to start the passkey registration with the
        user's device. The button is enabled if `user` is signed in and disabled otherwise.

    register_button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the register button. Emulates the `type` parameter of :func:`streamlit.button`.

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the register user process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the form.

    redirect : str or streamlit.navigation.page.StreamlitPage or None, default None
        The Streamlit page to redirect `user` to on successful registration. If str it should
        be the path, relative to the file passed to the ``streamlit run`` command, to the
        Python file containing the page to redirect to. See :func:`streamlit.switch_page`
        for more info. If None no redirect is performed.

    Other Parameters
    ----------------
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

    discoverability_label : str, default 'Discoverable Passkey'
        The label of the discoverability component.

    discoverability_component_type : Literal['toggle', 'radio'], default 'toggle'
        If the discoverability component should be rendered as a toggle switch or a radio button.

    discoverability_default_option : bool, default True
        The default option of the discoverability component. True means 'discoverable' and
        False 'non-discoverable'.

    discoverability_radio_button_options : tuple[str, str], default ('Discoverable', 'Non-Discoverable')
        The option names of the radio button if `discoverability_component_type` is set to 'radio'.

    discoverability_radio_button_horizontal : bool, default True
       The radio button options are rendered horizontally if True and vertically if False
       if `discoverability_component_type` is set to 'radio'.

    discoverability_help : str or None, default '__default__'
        The help text to display for the discoverability component. If '__default__' a sensible
        default help text is used and if None the help text is removed.

    Returns
    -------
    user_sign_in : streamlit_passwordless.UserSignIn or None
        The `user` modified with the `user.sign_in` entry with the newly registered passkey
        credential. None is returned if the user has not registered a passkey yet or if the
        registration failed.

    bool
        True if `user` has registered a passkey and False otherwise.
    """

    error_msg = ''
    banner_container = st.empty() if banner_container is None else banner_container
    if get_current_user:
        user = st.session_state.get(config.SK_USER) if user is None else user
    username, components_disabled = ('', True) if user is None else (user.username, False)

    with st.container(border=border):
        st.markdown(title)
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
                disabled=components_disabled,
                key=ids.BP_REGISTER_FORM_EXISTING_USER_CREDENTIAL_NICKNAME_TEXT_INPUT,
            )
        else:
            credential_nickname = username

        if with_discoverability:
            discoverable = _render_discoverability_component(
                label=discoverability_label,
                component_type=discoverability_component_type,
                default=discoverability_default_option,
                radio_button_option_names=discoverability_radio_button_options,
                radio_button_horizontal=discoverability_radio_button_horizontal,
                help_text=discoverability_help,
                form_type='existing_user',
                disabled=components_disabled,
            )
        else:
            discoverable = None

        if isinstance(user, db.models.User):
            from_db_user = True
            is_authenticated = True
            user = models.User.model_validate(user)
        else:
            from_db_user = False
            is_authenticated = False if user is None else user.is_authenticated

        if user is not None and is_authenticated:
            disabled = False
            register_token, error_msg = _create_register_token(
                client=client, user=user, discoverable=discoverable
            )
        else:
            disabled = True
            register_token = ''

        token, error, clicked = register_button(
            register_token=register_token,
            public_key=client.public_key,
            credential_nickname=credential_nickname.strip(),
            disabled=disabled,
            label=register_button_label,
            button_type=register_button_type,
            key=ids.BP_REGISTER_FORM_EXISTING_USER_SUBMIT_BUTTON,
        )

    if disabled or not clicked or user is None:
        return user, False

    if not token:
        if error:
            error_msg = f'Error creating passkey for user "{username}"!\nerror : {error}'
        else:
            error_msg = 'Unexpected error for missing register token!'

        logger.error(error_msg)
        core.display_banner_message(
            message=error_msg, message_type=core.BannerMessageType.ERROR, container=banner_container
        )
        return user, False

    # The passkey is still registered even though the sign in may fail!
    user_sign_in, _ = core.verify_sign_in(client=client, token=token)
    user.sign_in = user_sign_in
    if not from_db_user:
        st.session_state[config.SK_USER] = user

    final_error_msg = ''
    sign_in_failed_error_msg = (
        f'Passkey "{credential_nickname}" was registered, '
        'but the sign in attempt with registered passkey failed!'
    )
    if user_sign_in is None:
        final_error_msg = sign_in_failed_error_msg
        save_user_sign_in_to_db_ok = False
    else:
        if not user_sign_in.success:
            final_error_msg = sign_in_failed_error_msg

        save_user_sign_in_to_db_ok, error_msg = core.save_user_sign_in_to_database(
            session=db_session, user_sign_in=user_sign_in
        )
        if not save_user_sign_in_to_db_ok:
            final_error_msg = f'{final_error_msg}\n{error_msg}'

    if save_user_sign_in_to_db_ok:
        msg = f'Successfully registered passkey "{credential_nickname}" for user "{username}"!'
        logger.info(msg)
        core.display_banner_message(
            message=msg, message_type=core.BannerMessageType.SUCCESS, container=banner_container
        )
        if redirect:
            st.switch_page(redirect)
    else:
        logger.warning(final_error_msg)
        core.display_banner_message(
            message=final_error_msg,
            message_type=core.BannerMessageType.WARNING,
            container=banner_container,
        )

    return user, True

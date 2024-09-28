r"""The sign in form component."""

# Standard library
import logging

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import sign_in_button

from . import config, core, ids

logger = logging.getLogger(__name__)


def _process_user_sign_in_in_db(
    session: db.Session, user_sign_in: models.UserSignIn
) -> tuple[models.User | None, str, str]:
    r"""Process the user sign in entry in the database.

    The following session state keys are updated with data about the user that signed in:
    - config.SK_DB_USER : The database user object.
    - config.SK_USER : The user object.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    user_sign_in : streamlit_passwordless.models.UserSignIn
        Data from Bitwarden Passwordless about the user that signed in.

    Returns
    -------
    user : streamlit_passwordless.models.User or None
        The user object of the user that signed in. None is returned if no user with a
        matching user_id from `user_sign_in` was found in the database.

    username : str
        The name of the signed in user to display to the user. If the database user
        was not found the nickname of the passkey credential used for signing in is
        used instead.

    error_msg : str
        An error message to display to the user if there was an issue with saving
        the user sign in entry to the database.
    """

    user_sign_in_to_db = db.UserSignInCreate.model_validate(user_sign_in)

    try:
        db.create_user_sign_in(session=session, user_sign_in=user_sign_in_to_db, commit=True)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
    else:
        error_msg = ''

    try:
        db_user = db.get_user_by_user_id(session=session, user_id=user_sign_in.user_id)
        load_db_user_error = False
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        load_db_user_error = True
        db_user = None

    st.session_state[config.SK_DB_USER] = db_user

    if db_user is None:
        if not load_db_user_error:
            logger.warning(
                f'Signed in user (user_id={user_sign_in.user_id}, '
                f'credential_nickname={user_sign_in.credential_nickname}) '
                'was not found in local database!\n'
                'A mismatch between Bitwarden Passwordless.dev and local database has occurred!'
            )
        username = user_sign_in.credential_nickname
        user = None
    else:
        username = db_user.username
        user = models.User.model_validate(db_user)
        user.sign_in = user_sign_in

    st.session_state[config.SK_USER] = user

    return user, username, error_msg


def bitwarden_sign_in_form(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    with_alias: bool = True,
    with_discoverable: bool = True,
    with_autofill: bool = False,
    title: str = '#### Sign in',
    border: bool = True,
    submit_button_label: str = 'Sign in',
    button_type: core.ButtonType = 'primary',
    alias_label: str = 'Alias',
    alias_max_length: int | None = 50,
    alias_placeholder: str | None = 'john.doe@example.com',
    alias_help: str | None = '__default__',
) -> models.User | None:
    r"""Render the Bitwarden Passwordless sign in form.

    Allows the user to sign in to the application with a registered passkey.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless application.

    db_session : streamlit_passwordless.db.Session
        An active database session.

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

    border : bool, default True
        True if a border surrounding the form should be rendered and False
        to remove the border.

    submit_button_label : str, default 'Sign in'
        The label of the submit button.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    Other Parameters
    ----------------
    alias_label : str, default 'Alias'
        The label of the alias field.

    alias_max_length : int or None, default 50
        The maximum allowed number of characters of the alias field.
        If None the upper limit is removed.

    alias_placeholder : str or None, default 'john.doe@example.com'
        The placeholder of the alias field. If None the placeholder is removed.

    alias_help : str or None, default '__default__'
        The help text to display for the alias field. If '__default__' a sensible default
        help text will be used and if None the help text is removed.

    Returns
    -------
    user : streamlit_passwordless.User or None
        The user object of the user that signed in. None is returned if a user has not
        signed in yet or if the sign in failed and a user object could not be retrieved.
    """

    error_msg = ''
    help: str | None = None
    banner_container = st.empty()

    if with_alias is False and with_discoverable is False and with_autofill is False:
        with banner_container:
            error_msg = (
                f'At least one sign in method must be chosen!\n'
                f'*{with_alias=}*, *{with_discoverable=}*,  *{with_autofill=}*'
            )
            logger.error(error_msg)
            st.error(error_msg, icon=config.ICON_ERROR)
            return None

    with st.container(border=border):
        st.markdown(title)

        if with_alias:
            if alias_help == '__default__':
                help = (
                    'An alias of the user. If not supplied auto discover '
                    'of available credentials will be attempted.'
                )
            else:
                help = alias_help

            st.text_input(
                label=alias_label,
                placeholder=alias_placeholder,
                max_chars=alias_max_length,
                help=help,
                key=ids.BP_SIGN_IN_FORM_ALIAS_TEXT_INPUT,
            )

        token, error, clicked = sign_in_button(
            public_key=client.public_key,
            alias=st.session_state.get(ids.BP_SIGN_IN_FORM_ALIAS_TEXT_INPUT),
            with_discoverable=with_discoverable,
            with_autofill=with_autofill,
            label=submit_button_label,
            button_type=button_type,
            key=ids.BP_SIGN_IN_FORM_SUBMIT_BUTTON,
        )

    if not clicked:
        return None

    if not token and error:
        error_msg = f'Error signing in!\nerror : {error}'
        logger.error(error_msg)
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return None

    user_sign_in, error_msg = core.verify_sign_in(client=client, token=token)

    if user_sign_in is None or user_sign_in.success is False:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return None

    user, username, error_msg = _process_user_sign_in_in_db(
        session=db_session, user_sign_in=user_sign_in
    )

    with banner_container:
        if error_msg:
            st.warning(
                f'{error_msg} User {username} was still signed in.',
                icon=config.ICON_WARNING,
            )
        else:
            st.success(
                f'Successfully signed in user {username}',
                icon=config.ICON_SUCCESS,
            )

    return user

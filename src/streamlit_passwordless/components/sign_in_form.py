r"""The sign in form component."""

# Standard library
import logging

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessVerifiedUser
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import sign_in_button

from . import config, core, ids

logger = logging.getLogger(__name__)


def _process_user_sign_in_in_db(
    session: db.Session, verified_user: BitwardenPasswordlessVerifiedUser
) -> tuple[db.models.User | None, str, str]:
    r"""Process the user sign in entry in the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    verified_user : BitwardenPasswordlessVerifiedUser
        The verified user that signed in.

    Returns
    -------
    db_user : db.models.User or None
        The database user object. None is returned if no user with a matching
        user_id from `verified_user` was found.

    username : str
        The name of the signed in user to display to the user. If the database user
        was not found the nickname of the passkey credential used for signing in is
        used instead.

    error_msg : str
        An error message to display to the user if there was an issue with saving
        the user sign in entry to the database.
    """

    user_sign_in = db.UserSignInCreate(
        user_id=verified_user.user_id,
        sign_in_timestamp=verified_user.sign_in_timestamp,
        success=verified_user.success,
        origin=verified_user.origin,
        device=verified_user.device,
        country=verified_user.country,
        credential_nickname=verified_user.credential_nickname,
        credential_id=verified_user.credential_id,
        sign_in_type=verified_user.type,
        rp_id=verified_user.rp_id,
    )

    try:
        db.create_user_sign_in(session=session, user_sign_in=user_sign_in, commit=True)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
    else:
        error_msg = ''

    try:
        db_user = db.get_user_by_user_id(session=session, user_id=verified_user.user_id)
        load_db_user_error = False
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        load_db_user_error = True
        db_user = None

    if db_user is None:
        if not load_db_user_error:
            logger.warning(
                f'Signed in user (user_id={verified_user.user_id}, '
                f'credential_nickname={verified_user.credential_nickname}) '
                'was not found in local database!\n'
                'A mismatch between Bitwarden Passwordless.dev and local database has ocurred!'
            )
        username = verified_user.credential_nickname
    else:
        username = db_user.username

    return db_user, username, error_msg


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
) -> None:
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
            return

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
        return

    if not token and error:
        error_msg = f'Error signing in!\nerror : {error}'
        logger.error(error_msg)
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    verified_user, error_msg = core.verify_sign_in(client=client, token=token)

    if verified_user is None or verified_user.success is False:
        with banner_container:
            st.error(error_msg, icon=config.ICON_ERROR)
        return

    _, username, error_msg = _process_user_sign_in_in_db(
        session=db_session, verified_user=verified_user
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

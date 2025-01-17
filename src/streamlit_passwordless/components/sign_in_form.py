r"""The sign in form component."""

# Standard library
import logging
from typing import Any

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessClient
from streamlit_passwordless.bitwarden_passwordless.frontend import sign_in_button

from . import config, core, ids

logger = logging.getLogger(__name__)


def _get_user_from_db(
    session: db.Session, user_sign_in: models.UserSignIn
) -> tuple[models.User | None, str]:
    r"""Get the signed in user from the database.

    The following session state keys are updated with data about the user that signed in:
    - config.SK_DB_USER : The database user object.
    - config.SK_USER : The user object.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    user_sign_in : streamlit_passwordless.UserSignIn
        Data from Bitwarden Passwordless about the user that signed in.

    Returns
    -------
    user : streamlit_passwordless.User or None
        The user that signed in. None is returned if no user with a
        matching user_id from `user_sign_in` was found in the database.

    error_msg : str
        An error message with info if the user could not be loaded from the database.
        If no error occurred an empty string is returned.
    """

    db_user = None
    user = None
    try:
        db_user = db.get_user_by_user_id(session=session, user_id=user_sign_in.user_id)
        load_db_user_error = False
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        load_db_user_error = True
    else:
        error_msg = ''

    if db_user is None:
        if not load_db_user_error:
            logger.error(
                f'Signed in user (user_id={user_sign_in.user_id}, '
                f'credential_nickname={user_sign_in.credential_nickname}) '
                'was not found in local database!\n'
                'A mismatch between Bitwarden Passwordless.dev and local database has occurred!'
            )
            error_msg = (
                f'User trying to sign in with passkey {user_sign_in.credential_nickname} '
                'does not exist! Check the logs for more details.'
            )
    else:
        user = models.User.model_validate(db_user)

    st.session_state[config.SK_DB_USER] = db_user
    st.session_state[config.SK_USER] = user

    return user, error_msg


def _authorize_user(user: models.User, role: models.Role | int | None) -> tuple[models.User, str]:
    r"""Check if the `user` is authorized to sign in to the application.

    Parameters
    ----------
    user : streamlit_passwordless.User
        The user to authorize.

    role : streamlit_passwordless.Role or int or None
        The role to authorize `user` against. If the rank of the role of `user` is
        greater than or equal to the rank of `role` the `user` is authorized. If an
        integer is supplied it is assumed to be the rank of the role to authorize the
        user against. If None (the default) the user is authorized regardless of its role.
        The user must always be authenticated to be authorized.

    Returns
    -------
    user : streamlit_passwordless.User
        The authorized or not authorized `user`, where the `sign_in`
        attribute has been set to None if the user is not authorized.

    message : str
        An error message if the user was not authorized.
        An empty string is returned if the user was authorized.
    """

    if user.is_authorized(role=role):
        return user, ''

    user.sign_in = None

    if role is None:
        role_info = 'None'
    else:
        role_name = role.name if isinstance(role, models.Role) else ''
        role_rank = role.rank if isinstance(role, models.Role) else role
        role_info = f'Role(name={role_name}, rank={role_rank})'

    warning_msg = (
        f'User(username={user.username}, role=Role(name={user.role.name}, '
        f'rank={user.role.rank}) is not authorized to sign in '
        f'against role {role_info}'
    )
    logger.warning(warning_msg)

    return user, f'User {user.username} is not authorized to sign in!'


def _process_user_sign_in(
    token: str,
    error: dict[str, Any] | None,
    clicked: bool,
    client: BitwardenPasswordlessClient,
    session: db.Session,
    role: models.Role | int | None,
    banner_container: core.BannerContainer,
    redirect: core.Redirectable | None,
) -> tuple[models.User | None, bool]:
    r"""Process the user sign in and authorize the user.

    Parameters
    ----------
    token : str
        The verification token to be used by the Bitwarden Passwordless
        backend API to authenticate the sign in process.

    error : dict[str, Any] or None
        An error object from the frontend containing information if there
        was an error with the sign in process.

    clicked : bool
        True if the sign in button was clicked and False otherwise.

    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless backend API.

    session : streamlit_passwordless.db.Session
        An active database session.

    role : streamlit_passwordless.Role or int or None
        The role to authorize `user` against. If the rank of the role of `user` is
        greater than or equal to the rank of `role` the `user` is authorized. If an
        integer is supplied it is assumed to be the rank of the role to authorize the
        user against. If None (the default) the user is authorized regardless of its role.
        The user must always be authenticated to be authorized.

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the sign in process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the button or form.

    redirect : str or streamlit.navigation.page.StreamlitPage or None, default None
        The Streamlit page to redirect `user` to if authorized. If str it should be
        the path, relative to the file passed to the ``streamlit run`` command, to the
        Python file containing the page to redirect to. See :func:`streamlit.switch_page`
        for more info. If None no redirect is performed.

    Returns
    -------
    user : streamlit_passwordless.User or None
        The user that signed in and was authorized or not authorized. None is returned
        if no user with a matching user_id from `user_sign_in` was found in the database.

    success : bool
        True if the user was signed in and authorized without errors and False otherwise.
    """

    if not clicked:
        return None, False

    if not token and error:
        error_msg = f'Error signing in!\nerror : {error}'
        logger.error(error_msg)
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )
        return None, False

    user_sign_in, error_msg = core.verify_sign_in(client=client, token=token)

    if user_sign_in is None or user_sign_in.success is False:
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )
        return None, False

    user, error_msg = _get_user_from_db(session=session, user_sign_in=user_sign_in)
    if user is None:
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )
        return user, False
    else:
        user.sign_in = user_sign_in

    user, error_msg = _authorize_user(user=user, role=role)
    if error_msg:
        user.sign_in = None
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )
        return user, False

    success, error_msg = core.save_user_sign_in_to_database(
        session=session, user_sign_in=user_sign_in
    )

    if not success:
        user.sign_in = None
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )
        return user, success

    if redirect:
        st.switch_page(redirect)

    core.display_banner_message(
        message=f'Successfully signed in user {user.username}',
        message_type=core.BannerMessageType.SUCCESS,
        container=banner_container,
    )

    return user, success


def bitwarden_sign_in_form(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    role: models.Role | int | None = None,
    with_alias: bool = True,
    with_discoverable: bool = True,
    with_autofill: bool = False,
    title: str = '#### Sign in',
    border: bool = True,
    submit_button_label: str = 'Sign in',
    button_type: core.ButtonType = 'primary',
    banner_container: core.BannerContainer | None = None,
    redirect: core.Redirectable | None = None,
    alias_label: str = 'Alias',
    alias_max_length: int | None = 50,
    alias_placeholder: str | None = 'john.doe@example.com',
    alias_help: str | None = '__default__',
) -> tuple[models.User | None, bool]:
    r"""Render the Bitwarden Passwordless sign in form.

    Allows the user to sign in to the application with a registered passkey.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless application.

    db_session : streamlit_passwordless.db.Session
        An active database session.

    role : streamlit_passwordless.Role or int or None, default None
        The role to authorize `user` against. If the rank of the role of `user` is
        greater than or equal to the rank of `role` the `user` is authorized. If an
        integer is supplied it is assumed to be the rank of the role to authorize the
        user against. If None (the default) the user is authorized regardless of its role.
        The user must always be authenticated to be authorized.

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

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the sign in process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the form.

    redirect : str or streamlit.navigation.page.StreamlitPage or None, default None
        The Streamlit page to redirect `user` to if authorized. If str it should be
        the path, relative to the file passed to the ``streamlit run`` command, to the
        Python file containing the page to redirect to. See :func:`streamlit.switch_page`
        for more info. If None no redirect is performed.

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

    success : bool
        True if the user was signed in and authorized without errors and False otherwise.

    Raises
    ------
    streamlit_passwordless.StreamlitPasswordlessError
        If no sign in method is chosen i.e. `with_alias` is False,
        `with_discoverable` is False and `with_autofill` is False.
    """

    if with_alias is False and with_discoverable is False and with_autofill is False:
        error_msg = (
            f'At least one sign in method must be chosen!\n'
            f'bitwarden_sign_in_form({with_alias=}, {with_discoverable=}, {with_autofill=})'
        )
        logger.error(error_msg)
        raise exceptions.StreamlitPasswordlessError(
            message=error_msg,
            data={
                'with_alias': with_alias,
                'with_discoverable': with_discoverable,
                'with_autofill': with_autofill,
            },
        )

    help: str | None = None
    banner_container = st.empty() if banner_container is None else banner_container

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

    user, success = _process_user_sign_in(
        token=token,
        error=error,
        clicked=clicked,
        client=client,
        session=db_session,
        role=role,
        banner_container=banner_container,
        redirect=redirect,
    )

    return user, success


def bitwarden_sign_in_button(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    role: models.Role | int | None = None,
    with_discoverable: bool = True,
    with_autofill: bool = False,
    button_label: str = 'Sign in',
    button_type: core.ButtonType = 'primary',
    banner_container: core.BannerContainer | None = None,
    redirect: core.Redirectable | None = None,
) -> tuple[models.User | None, bool]:
    r"""Render the Bitwarden Passwordless sign in button.

    Allows the user to sign in to the application with a discoverable passkey.
    Similar to :func:`bitwarden_sign_in_form`, but without the possibility to
    sign in with user_id, alias or a non-discoverable passkey.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        The Bitwarden Passwordless client to use for interacting with
        the Bitwarden Passwordless application.

    db_session : streamlit_passwordless.db.Session
        An active database session.

    role : streamlit_passwordless.Role or int or None, default None
        The role to authorize `user` against. If the rank of the role of `user` is
        greater than or equal to the rank of `role` the `user` is authorized. If an
        integer is supplied it is assumed to be the rank of the role to authorize the
        user against. If None (the default) the user is authorized regardless of its role.
        The user must always be authenticated to be authorized.

    with_discoverable : bool, default True
        If True the browser's native UI prompt will be used to select the passkey to use for
        signing in. If False the sign in method is disabled. If `alias` is specified it will
        override this sign in method.

    with_autofill : bool, default False
        If True the browser's native autofill UI will be used to select the passkey to use for
        signing in. If False the sign in method is disabled. This method of signing in is
        overridden if `alias` specified or `with_discoverable` is True.

    button_label : str, default 'Sign in'
        The label of the button.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the sign in process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the button.

    redirect : str or streamlit.navigation.page.StreamlitPage or None, default None
        The Streamlit page to redirect `user` to if authorized. If str it should be
        the path, relative to the file passed to the ``streamlit run`` command, to the
        Python file containing the page to redirect to. See :func:`streamlit.switch_page`
        for more info. If None no redirect is performed.

    Returns
    -------
    user : streamlit_passwordless.User or None
        The user that signed in. None is returned if a user has not signed
        in yet or if the sign in failed and a user could not be retrieved.

    success : bool
        True if the user was signed in and authorized without errors and False otherwise.

    Raises
    ------
    streamlit_passwordless.StreamlitPasswordlessError
        If no sign in method is chosen i.e. `with_discoverable` is False
        and `with_autofill` is False.
    """

    if with_discoverable is False and with_autofill is False:
        error_msg = (
            f'At least one sign in method must be chosen!\n'
            f'bitwarden_sign_in_button({with_discoverable=}, {with_autofill=})'
        )
        logger.error(error_msg)
        raise exceptions.StreamlitPasswordlessError(
            message=error_msg,
            data={'with_discoverable': with_discoverable, 'with_autofill': with_autofill},
        )

    banner_container = st.empty() if banner_container is None else banner_container

    token, error, clicked = sign_in_button(
        public_key=client.public_key,
        with_discoverable=with_discoverable,
        with_autofill=with_autofill,
        label=button_label,
        button_type=button_type,
        key=ids.BP_SIGN_IN_BUTTON,
    )

    user, success = _process_user_sign_in(
        token=token,
        error=error,
        clicked=clicked,
        client=client,
        session=db_session,
        role=role,
        banner_container=banner_container,
        redirect=redirect,
    )

    return user, success

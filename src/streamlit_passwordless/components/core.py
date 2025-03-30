r"""Helper functions and core components that can be used by other components."""

# Standard library
import logging
from enum import StrEnum
from functools import partial
from typing import Literal, Sequence, TypeAlias

# Third party
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.navigation.page import StreamlitPage

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.backend import (
    BitwardenPasswordlessClient,
)

from . import config

BannerContainer: TypeAlias = DeltaGenerator
ButtonType: TypeAlias = Literal['primary', 'secondary']
Redirectable: TypeAlias = StreamlitPage | str
logger = logging.getLogger(__name__)


class FormField(StrEnum):
    r"""The text input form fields defined in Streamlit Passwordless.

    Members
    -------
    USERNAME
        The username of a user.

    DISPLAYNAME
        The displayname of a user.

    AD_USERNAME
        The active directory username of a user.

    EMAIL
        An email address of a user.
    """

    USERNAME = 'username'
    DISPLAYNAME = 'displayname'
    AD_USERNAME = 'ad_username'
    EMAIL = 'email'


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


def save_user_sign_in_to_database(
    session: db.Session, user_sign_in: models.UserSignIn
) -> tuple[bool, str]:
    r"""Save the user sign in entry to the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    user_sign_in : streamlit_passwordless.UserSignIn
        Data from Bitwarden Passwordless about the user that signed in.

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


def get_user_from_database(
    session: db.Session, username: str, disabled: bool | None = None
) -> tuple[db.models.User | None, str]:
    r"""Get a user from the database.

    Updates the session state key `streamlit_passwordless.SK_DB_USER`
    with the user object from the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    username : str
        The username of the user to retrieve from the database.

    disabled : bool or None, default None
        Specify True to retrieve disabled users and False for enabled users.
        If None filtering by disabled or enabled user is omitted.

    Returns
    -------
    user : streamlit_passwordless.db.models.User or None
        The user matching `username`. None is returned if no user was found.

    error_msg : str
        An error message to display to the user if there was an issue with retrieving
        the user from the database. If no error occurred an empty string is returned.
    """

    try:
        user = db.get_user_by_username(session=session, username=username, disabled=disabled)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        user = None
    else:
        error_msg = ''

    st.session_state[config.SK_DB_USER] = user

    return user, error_msg


def create_user_in_database(
    session: db.Session,
    user: models.User,
    custom_roles: Sequence[db.models.CustomRole] | None = None,
) -> tuple[bool, str]:
    r"""Create a new user in the database.

    Parameters
    ----------
    session : streamlit_passwordless.db.Session
        An active database session.

    user : models.User
        The user to save to the database.

    custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole] or None, default None
        The custom roles from the active database `session` to associate with the user.
        If provided these roles will take precedence over the custom roles defined on
        `user` and avoids a database lookup since the custom roles already exist in the `session`.

    Returns
    -------
    success : bool
        True if the user was successfully saved to the database and False otherwise.

    error_msg : str
        An error message to display to the user if there was an issue with creating the user
        in the database. If no error occurred an empty string is returned.
    """

    try:
        db.create_user(session=session, user=user, custom_roles=custom_roles, commit=True)
    except exceptions.DatabaseCreateUserError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        success = False
    else:
        error_msg = ''
        success = True

    return success, error_msg


def update_user_in_database(session: db.Session, user: db.models.User) -> tuple[bool, str]:
    r"""Update an existing user in the database.

    Parameters
    ----------
    session : streamlit_passwordless.db.Session
        An active database session.

    user : models.User
        The user to update.

    Returns
    -------
    success : bool
        True if the user was successfully updated and False otherwise.

    error_msg : str
        An error message to display to the user if there was an issue with updating
        the user in the database. If no error occurred an empty string is returned.
    """

    try:
        db.commit(session, error_msg=f'Could not update {user.username}!')
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        success = False
    else:
        error_msg = ''
        success = True

    return success, error_msg


def get_all_roles_from_database(session: db.Session) -> tuple[Sequence[db.models.Role], str]:
    r"""Get all roles from the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    Returns
    -------
    db_roles : Sequence[streamlit_passwordless.db.models.Role]
        The roles loaded from the database.

    error_msg : str
        An error message to display to the user if there was an issue with retrieving
        the roles from the database. If no error occurred an empty string is returned.
    """

    try:
        db_roles = db.get_all_roles(session=session, as_df=False)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        db_roles = []
    else:
        error_msg = ''

    return db_roles, error_msg


def get_all_custom_roles_from_database(
    session: db.Session,
) -> tuple[Sequence[db.models.CustomRole], str]:
    r"""Get all custom roles from the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    Returns
    -------
    db_custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole]
        The custom roles from the database.

    error_msg : str
        An error message to display to the user if there was an issue with retrieving
        the custom roles from the database. If no error occurred an empty string is returned.
    """

    try:
        db_custom_roles = db.get_all_custom_roles(session=session, as_df=False)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        db_custom_roles = []
    else:
        error_msg = ''

    return db_custom_roles, error_msg


def get_email_from_database(
    session: db.Session, email: str, load_user: bool = False
) -> tuple[db.models.Email | None, str]:
    r"""Get an email from the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    email : str
        The email address to retrieve from the database.

    load_user : bool, default False
        If True the user that that the email belongs to will also be loaded from the database.

    Returns
    -------
    db_email : streamlit_passwordless.db.models.Email or None
        The email address matching `email` or None if an email was not found.

    error_msg : str
        An error message to display to the user if there was an issue with retrieving
        the email from the database. If no error occurred an empty string is returned.
    """

    try:
        db_email = db.get_email(session=session, email=email, load_user=load_user)
    except exceptions.DatabaseError as e:
        logger.error(e.detailed_message)
        error_msg = e.displayable_message
        db_email = None
    else:
        error_msg = ''

    return db_email, error_msg


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


def process_form_validation_errors(
    validation_errors: dict[str, str],
    banner_container_mapping: dict[str, BannerContainer],
    default_banner_container: BannerContainer | None = None,
) -> None:
    r"""Process form validation errors and display them in an error banner.

    Parameters
    ----------
    validation_errors : dict[str, str]
        A mapping of the field name to its error message.

    banner_container_mapping : dict[str, streamlit_passwordless.BannerContainer]
        A mapping of the field name to its banner container.

    default_banner_container : streamlit_passwordless.BannerContainer or None, default None
        The default banner container to use if a field does not have a matching entry in
        `banner_container_mapping`. If None the banner will be displayed at the location
        of the page where this function is called.
    """

    for field_name, error_msg in validation_errors.items():
        bc = banner_container_mapping.get(field_name, default_banner_container)
        display_banner_message(
            message=error_msg, message_type=BannerMessageType.ERROR, container=bc
        )

r"""The delete user button and its callback functions."""

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless.authorization import sign_out
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.models import AdminRole, Role, User

from . import config, core, ids


def _can_delete_user(
    user_id: str, signed_in_user: User | None, allow_delete_self: bool, authorized_for_role: Role
) -> None:
    r"""Check if a user is allowed to delete a user.

    Parameters
    ----------
    user_id : str
        The unique ID of the user to delete.

    signed_in_user : streamlit_passwordless.User or None
        The signed in user performing the delete operation.

    allow_delete_self : bool
        If True `signed_in_user` is allowed to delete itself.

    authorized_for_role : streamlit_passwordless.Role
        The minimum role of `signed_in_user` to be authorized to delete a user.
    """

    if signed_in_user is None or not signed_in_user.is_authenticated:
        error_msg = 'A user must be signed in to be able to delete a user!'
        st.session_state[config.SK_DELETE_USER_VALIDATION_ERRORS] = error_msg
        return

    error_msg = ''
    displayname = n if (n := signed_in_user.displayname) is not None else signed_in_user.username

    if signed_in_user.is_authorized(role=authorized_for_role):
        if signed_in_user.user_id == user_id:
            if allow_delete_self:
                st.session_state[config.SK_DELETE_USER_SELF] = True
            else:
                error_msg = f'Cannot delete signed in user: "{displayname}"!'
        else:
            pass

    else:
        error_msg = f'User "{displayname}" is not authorized to delete users'

    st.session_state[config.SK_DELETE_USER_VALIDATION_ERRORS] = error_msg


def _delete_user(
    client: BitwardenPasswordlessClient, db_session: db.Session, user: db.models.User
) -> tuple[bool, str]:
    r"""Delete a user from Bitwarden Passwordless and the database.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    user : streamlit_passwordless.db.models.User
        The user to delete.

    Returns
    -------
    success : bool
        True if the `user` was successfully deleted and False otherwise.

    error_msg : str
        An error message to display to the user if there was an issue with deleting
        the user. If no error occurred an empty string is returned.
    """

    success, error_msg = core.delete_user_from_bitwarden_passwordless(
        client=client, user_id=user.user_id
    )
    if success:
        success, error_msg = core.delete_user_in_database(session=db_session, user=user)

    return success, error_msg


def delete_user_button(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    user: db.models.User | None,
    allow_delete_self: bool = False,
    authorized_for_role: Role = AdminRole,
    label: str = 'Delete User',
    button_type: core.ButtonType = 'primary',
    help: str | None = 'Delete a user from the database and Bitwarden Passwordless.',
    use_container_width: bool = False,
    banner_container: core.BannerContainer | None = None,
    key=ids.DELETE_USER_BUTTON,
) -> tuple[bool, bool]:
    r"""Render the button for deleting a user.

    The user is deleted from Bitwarden Passwordless and the local database.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    user : streamlit_passwordless.db.models.User or None
        The user to delete. If None the delete button is disabled.

    allow_delete_self : bool, default False
        If True the signed in user is allowed to delete itself.

    authorized_for_role : streamlit_passwordless.Role, default streamlit_passwordless.AdminRole
        The minimum role of the signed in user to be authorized to delete a user.

    label : str, default 'Delete User'
        The label of the delete button.

    button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the delete button. Emulates the `type` parameter of :func:`streamlit.button`.

    help : str or None, default 'Delete a user from the database and Bitwarden Passwordless.'
        The help text to display for the delete button. If None the help text is removed.

    use_container_width : bool, default False
        If True the button will take up the entire width of its enclosing container.

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the delete user process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the delete button.

    key : str, default streamlit_passwordless.components.ids.DELETE_USER_BUTTON
        The unique identifier of the button. Each component on a page must have a unique key.

    Returns
    -------
    clicked : bool
        True if the button was clicked and False otherwise.

    success : bool
        True if the user deletion was successful and False otherwise.
    """

    banner_container = st.empty() if banner_container is None else banner_container
    signed_in_user = config.get_current_user()

    if user is None:
        disabled = True
        user_id = ''
        username = ''
    else:
        user_id = user.user_id
        username = user.username
        disabled = True if signed_in_user is None else not signed_in_user.is_authenticated

    clicked = st.button(
        label=label,
        type=button_type,
        disabled=disabled,
        on_click=_can_delete_user,
        kwargs={
            'user_id': user_id,
            'signed_in_user': signed_in_user,
            'allow_delete_self': allow_delete_self,
            'authorized_for_role': authorized_for_role,
        },
        use_container_width=use_container_width,
        help=help,
        key=key,
    )

    if not clicked:
        return False, False

    if error_msg := st.session_state.get(config.SK_DELETE_USER_VALIDATION_ERRORS):
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )

        return True, False

    if user is None:
        core.display_banner_message(
            message='Cannot delete non-existing user!',
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )

        return True, False

    success, error_msg = _delete_user(client=client, db_session=db_session, user=user)
    if not success:
        core.display_banner_message(
            message=error_msg,
            message_type=core.BannerMessageType.ERROR,
            container=banner_container,
        )

        return True, False

    if st.session_state.get(config.SK_DELETE_USER_SELF, False):
        sign_out(user=signed_in_user)

    core.display_banner_message(
        message=f'Successfully deleted user {username}!',
        message_type=core.BannerMessageType.SUCCESS,
        container=banner_container,
    )

    return True, True

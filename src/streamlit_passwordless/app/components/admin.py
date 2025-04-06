r"""The components of the admin app."""

# Standard library
from time import sleep
from typing import Sequence

# Third party
import pandas as pd
import streamlit as st

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless.app.components import keys
from streamlit_passwordless.app.logic.admin import get_selectable_users_from_database
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.components import create_user_form


@st.dialog(title='Create User')
def create_user_dialog_form(
    db_session: db.Session, on_success_exit_after_n_seconds: int | None = 2
) -> None:
    r"""Render the form for creating a new user in a dialog frame.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    on_success_exit_after_n_seconds : int, default 2
        The dialog form will close automatically after n number of seconds after a successful
        user creation. If None the dialog form will not close automatically.
    """

    created_user = create_user_form(
        db_session=db_session, with_ad_username=True, border=False, title=''
    )
    if created_user is not None:
        get_selectable_users_from_database(db_session=db_session)

        if on_success_exit_after_n_seconds is not None:
            sleep(on_success_exit_after_n_seconds)

        st.rerun(scope='app')


def user_state_radio_button(
    label: str = 'User State',
    default_disabled: bool = False,
    key: str = keys.ADMIN_USER_STATE_RADIO_BUTTON,
) -> bool:
    r"""Render the user state radio button.

    A user can be either enabled or disabled.

    Parameters
    ----------
    label : str, default 'User State'
        The label of the radio button.

    default_enabled : bool, default True
        True if the radio button will be set to 'enabled' on first render and
        False for 'disabled'.

    key : str, default streamlit_passwordless.app.keys.ADMIN_USER_STATE_RADIO_BUTTON
        The unique identifier of the component. Each component on a page must have a unique key.
    """

    return st.radio(
        label=label,
        options=(False, True),
        index=1 if default_disabled else 0,
        format_func=lambda x: 'Enabled' if x is False else 'Disabled',
        horizontal=True,
        key=key,
    )


def create_user_button(
    db_session: db.Session,
    label: str = 'Create User',
    disabled: bool = False,
    key=keys.ADMIN_CREATE_USER_BUTTON,
) -> bool:
    r"""Render the button for creating an new user.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    label : str, default 'Create User'
        The label of the button.

    disabled : bool, default False
        If True the component is disabled from user interaction.

    key : str, default streamlit_passwordless.app.keys.ADMIN_CREATE_USER_BUTTON
        The unique identifier of the component. Each component on a page must have a unique key.

    Returns
    -------
    bool
        True if the button was clicked and False otherwise.
    """

    return st.button(
        label=label,
        key=key,
        disabled=disabled,
        help='Create a new user in the database.',
        on_click=create_user_dialog_form,
        kwargs={'db_session': db_session},
    )


def refresh_users_button(
    db_session: db.Session,
    label: str = 'Refresh Users',
    disabled: bool = False,
    key=keys.ADMIN_REFRESH_USERS_BUTTON,
) -> bool:
    r"""Render button for refreshing the selectable users.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    label : str, default 'Refresh Users'
        The label of the button.

    disabled : bool, default False
        If True the component is disabled from user interaction.

    key : str, default streamlit_passwordless.app.keys.ADMIN_REFRESH_USERS_BUTTON
        The unique identifier of the component. Each component on a page must have a unique key.

    Returns
    -------
    bool
        True if the button was clicked and False otherwise.
    """

    return st.button(
        label=label,
        disabled=disabled,
        key=key,
        help='Load users from the database.',
        on_click=get_selectable_users_from_database,  # type: ignore
        kwargs={'db_session': db_session},
    )


def delete_user_button(
    client: BitwardenPasswordlessClient,
    db_session: db.Session,
    label: str = 'Delete User',
    disabled: bool = False,
    key=keys.ADMIN_DELETE_USER_BUTTON,
) -> bool:
    r"""Render the button for deleting a user.

    Parameters
    ----------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    db_session : streamlit_passwordless.db.Session
        An active session to the Streamlit Passwordless database.

    label : str, default 'Delete User'
        The label of the button.

    disabled : bool, default False
        If True the component is disabled from user interaction.

    key : str, default streamlit_passwordless.app.keys.ADMIN_DELETE_USER_BUTTON
        The unique identifier of the component. Each component on a page must have a unique key.

    Returns
    -------
    bool
        True if the button was clicked and False otherwise.
    """

    return st.button(
        label=label,
        key=key,
        disabled=disabled,
        help='Delete a user from the database and Bitwarden Passwordless.dev.',
    )


def user_role_multiselect(
    roles: Sequence[db.models.Role],
    label: str = 'Roles',
    placeholder: str = 'Select the roles to filter by',
    key=keys.ADMIN_USER_ROLE_MULTISELECT,
) -> list[db.models.Role]:
    r"""Render the multi-selectbox of the roles to use for filtering the selectable users.

    Parameters
    ----------
    roles : Sequence[streamlit_passwordless.db.models.Role]
        The selectable roles.

    label : str, default 'Roles'
        The label of the multi-selectbox.

    placeholder : str, default 'Select the roles to filter by'
        The placeholder to display if no role is chosen.

    key : str, default streamlit_passwordless.app.keys.ADMIN_USER_ROLE_MULTISELECT
        The unique identifier of the component. Each component on a page must have a unique key.

    Returns
    -------
    list[streamlit_passwordless.db.models.Role]
        The selected roles.
    """

    return st.multiselect(
        label=label,
        options=roles,
        format_func=lambda r: r.name,
        key=key,
        placeholder=placeholder,
        help='Filter the users by roles.',
    )


def user_selectbox(
    df: pd.DataFrame, preselected_user: int | None = None, placeholder: str = 'Choose a user'
) -> str:
    r"""Render the selectbox for selecting the user to process.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame with the user info to provide for selecting a user. The index column
        should contain the user_id:s of the users. The columns of the DataFrame should be the
        searchable columns "username, "displayname", and "ad_username".

    preselected_user : int or None, default None
        The pre-selected user on first render of the component. 0 means the first user of `df`.
        If None no user is pre-selected and the value of `placeholder` is displayed instead.

    placeholder : str, default 'Choose a user'
        The placeholder to display if no user is chosen.

    key : str, default streamlit_passwordless.app.keys.ADMIN_USER_SELECTBOX
        The unique identifier of the component. Each component on a page must have a unique key.

    Returns
    -------
    str
        The selected user.
    """

    def format_user_display_text(user_id: str) -> str:
        r"""The text to display instead of the user_id in the selectbox."""

        s = df.loc[user_id, ['username', 'displayname', 'ad_username']]  # type: ignore

        return f'{s["username"]} | {s["displayname"]} | {s["ad_username"]}'

    nr_users = df.shape[0]
    label = (
        f'Select from {nr_users} user{"s" if nr_users > 0 else ""} '
        '(username | displayname | ad_username)'
    )
    return st.selectbox(
        label=label,
        options=df.index,
        index=preselected_user,  # type: ignore
        format_func=format_user_display_text,
        key=keys.ADMIN_USER_SELECTBOX,
        placeholder=placeholder,
        help='Search for a user by username, displayname or ad_username',
    )

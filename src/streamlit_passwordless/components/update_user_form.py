r"""The update user form component and its callback functions."""

# Standard library
from datetime import datetime
from typing import Sequence
from zoneinfo import ZoneInfo

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless.models import UserID

from . import config, core, ids


def _validate_form(db_session: db.Session, current_username: str) -> None:
    r"""Validate the input fields of the update user form.

    Updates the following session state keys:
    - `streamlit_passwordless.SK_UPDATE_USER_FORM_IS_VALID` :
        True if the form validation passed and False otherwise.

    - `streamlit_passwordless.SK_UPDATE_USER_FORM_VALIDATION_ERRORS` :
        A dictionary mapping of the user form field name to its error message.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    current_username : str
        The current username of the user.
    """

    form_is_valid = True
    validation_errors = {}

    validation_error_field = core.FormField.USERNAME
    if username := st.session_state[ids.UPDATE_USER_FORM_USERNAME_TEXT_INPUT]:

        if (new_username := username.strip().casefold()) != current_username:
            db_user, error_msg = core.get_user_from_database(
                session=db_session, username=new_username
            )

            if error_msg:  # DatabaseError
                form_is_valid = False
                validation_errors[validation_error_field] = error_msg
            elif db_user is not None:
                form_is_valid = False
                validation_errors[validation_error_field] = f'User {username} already exists!'
            else:
                pass

    else:
        validation_errors[validation_error_field] = 'The username field is required!'

    st.session_state[config.SK_UPDATE_USER_FORM_VALIDATION_ERRORS] = validation_errors
    st.session_state[config.SK_UPDATE_USER_FORM_IS_VALID] = form_is_valid


def _updated_user(
    user: db.models.User,
    username: str,
    with_displayname: bool,
    displayname: str | None,
    with_ad_username: bool,
    ad_username: str | None,
    with_role: bool,
    role_id: int,
    with_custom_roles: bool,
    custom_roles: Sequence[db.models.CustomRole] | None,
    with_disabled: bool,
    disabled: bool,
    updated_by_user_id: UserID | None,
) -> bool:
    r"""Update the fields of the user.

    Parameters
    ----------
    user : streamlit_passwordless.db.User
        The user to update.

    username : str
        The new username of the user.

    with_displayname : bool, default True
        If True the displayname field is updatable.

    displayname : str or None
        The new displayname of the user.

    with_ad_username : bool, default False
        If True the ad_username field is updatable.

    ad_username : str or None
        The new active directory username of the user.

    with_role : bool, default True
        If True the role of the user is updatable.

    role_id : int
        The new role_id of the user.

    with_custom_roles : bool, default False
        If True the custom roles of the user are updatable.

    custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole] or None
        The new custom roles of the user.

    with_disabled_toggle : bool, default True
        If True the enabled or disabled state of the user is updatable.

    disabled : bool
        The new state of the disabled field of the user.

    updated_by_user_id : streamlit_passwordless.UserID or None
        The ID of the user that is updating the `user` to update.

    Returns
    -------
    bool
        True if any field of `user` was updated and False otherwise.
    """

    if (new_username := username.strip()) != user.username:
        user.username = new_username
        username_updated = True
    else:
        username_updated = False

    if with_displayname:
        new_displayname = None if displayname is None else displayname.strip()
        displayname_updated = user.displayname != new_displayname

        if displayname_updated:
            user.displayname = new_displayname
    else:
        displayname_updated = False

    if with_ad_username:
        new_ad_username = None if ad_username is None else ad_username.strip()
        ad_username_updated = user.ad_username != new_ad_username

        if ad_username_updated:
            user.ad_username = new_ad_username
    else:
        ad_username_updated = False

    if with_role:
        role_updated = user.role_id != role_id

        if role_updated:
            user.role_id = role_id
    else:
        role_updated = False

    if with_custom_roles:
        new_custom_roles = {cr.name: cr for cr in custom_roles} if custom_roles else {}

        new_custom_roles_set = set(new_custom_roles.keys())
        old_custom_roles_set = set(user.custom_roles.keys())
        diff = set.union(
            new_custom_roles_set.difference(old_custom_roles_set),
            old_custom_roles_set.difference(new_custom_roles_set),
        )
        custom_roles_updated = True if diff else False

        if custom_roles_updated:
            user.custom_roles = new_custom_roles
    else:
        custom_roles_updated = False

    if with_disabled:
        disabled_updated = user.disabled != disabled

        if disabled_updated:
            user.disabled = disabled
            user.disabled_at = datetime.now(tz=ZoneInfo('UTC')) if disabled else None
    else:
        disabled_updated = False

    user.updated_by = updated_by_user_id

    return any(
        [
            username_updated,
            displayname_updated,
            ad_username_updated,
            role_updated,
            custom_roles_updated,
            disabled_updated,
        ]
    )


def update_user_form(
    db_session: db.Session,
    user: db.models.User,
    with_displayname: bool = True,
    with_ad_username: bool = True,
    with_role: bool = True,
    with_custom_roles: bool = True,
    with_disabled_toggle: bool = True,
    roles: Sequence[db.models.Role] | None = None,
    custom_roles: Sequence[db.models.CustomRole] | None = None,
    title: str = '#### Update user',
    border: bool = True,
    submit_button_label: str = 'Update User',
    submit_button_type: core.ButtonType = 'primary',
    clear_on_submit: bool = True,
    banner_container: core.BannerContainer | None = None,
    updated_by_user_id: UserID | None = None,
    username_label: str = 'Username',
    username_max_length: int | None = 50,
    username_placeholder: str | None = 'john.doe',
    username_help: str | None = 'A unique identifier for the user.',
    displayname_label: str = 'Displayname',
    displayname_max_length: int | None = 50,
    displayname_placeholder: str | None = 'John Doe',
    displayname_help: str | None = 'A descriptive name of the user.',
    ad_username_label: str = 'Active Directory Username',
    ad_username_max_length: int | None = 50,
    ad_username_placeholder: str | None = 'ad.john.doe',
    ad_username_help: str | None = 'The active directory username of the user.',
    role_label: str = 'Role',
    role_placeholder: str = 'Choose a role',
    role_help: str | None = 'The role of the user.',
    custom_roles_label: str = 'Custom Roles',
    custom_roles_placeholder: str = 'Choose a custom role',
    custom_roles_max_selections: int | None = None,
    custom_roles_help: str | None = 'The custom roles to associate with the user.',
    disabled_toggle_label: str = 'Disabled User',
    disabled_toggle_help: str | None = 'If the user should be created as disabled or enabled.',
) -> tuple[db.models.User, bool]:
    r"""Render the update user form.

    Update information about an existing user in the database.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    user : streamlit_passwordless.db.User
        The user to update.

    with_displayname : bool, default True
        If True the displayname field is added to the form to enable to
        edit the displayname of the user.

    with_ad_username : bool, default False
        If True the ad_username field is added to the form to enable to
        edit the active directory username of the user.

    with_role : bool, default True
        If True the role selectbox is added to the form to enable to change
        the role of the user.

    with_custom_roles : bool, default False
        If True the custom roles multiselectbox is added to the form to enable
        to change the custom roles of the user.

    with_disabled_toggle : bool, default True
        If True the disabled user toggle switch will be added to the form, which enables
        changing the state of the user between enabled and disabled.

    roles : Sequence[streamlit_passwordless.Role] or None, default None
        The available roles that can be assigned to the user. If None the defined
        roles in the database will be loaded and made available for selection.

    custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole] or None, default None
        The available custom roles that can be assigned to the user. If None the defined
        custom roles in the database will be loaded and made available for selection.

    title : str, default '#### Update User'
        The title of the update user form. Markdown is supported.

    border : bool, default True
        If True a border will be rendered around the form.

    submit_button_label : str, default 'Create User'
        The label of the form submit button.

    submit_button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the submit button. Emulates the `type` parameter of :func:`streamlit.button`.

    clear_on_submit : bool, default True
        If True the form fields will be cleared when the submit form button is clicked.

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the update user process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the form.

    updated_by_user_id : streamlit_passwordless.UserID or None, default None
        The ID of the user that is updating the `user` to update.
        If None the ID of the currently signed in user is used.

    Other Parameters
    ----------------
    username_label : str, default 'Username'
        The label of the username field.

    username_max_length : int or None, default 50
        The maximum allowed number of characters of the username field.
        If None the upper limit is removed.

    username_placeholder : str or None, default 'john.doe'
        The placeholder of the username field. If None the placeholder is removed.

    username_help : str or None, default 'A unique identifier for the user.'
        The help text to display for the username field. If None the help text is removed.

    displayname_label : str, default 'Displayname'
        The label of the displayname field.

    displayname_max_length : int or None, default 50
        The maximum allowed number of characters of the displayname field.
        If None the upper limit is removed.

    displayname_placeholder : str or None, default 'John Doe'
        The placeholder of the displayname field. If None the placeholder is removed.

    displayname_help : str or None, default 'A descriptive name of the user.'
        The help text to display for the displayname field. If None the help text is removed.

    ad_username_label : str, default 'Active Directory Username'
        The label of the ad_username field.

    ad_username_max_length : int or None, default 50
        The maximum allowed number of characters of the ad_username field.
        If None the upper limit is removed.

    ad_username_placeholder : str or None, default 'ad.john.doe'
        The placeholder of the ad_username field. If None the placeholder is removed.

    ad_username_help : str or None, default 'The active directory username of the user.'
        The help text to display for the ad_username field. If None the help text is removed.

    role_label : str, default 'Role'
        The label of the role selectbox.

    role_placeholder : str, default 'Choose a role'
        The placeholder of the role selectbox if a role is not preselected.

    role_help: str or None, default 'The role of the user.'
        The help text to display for the role selectbox. If None the help text is removed.

    custom_roles_label : str, default 'Custom Roles',
        The label of the custom roles multiselectbox.

    custom_roles_placeholder : str, default 'Choose a custom role'
        The placeholder of the custom roles multiselectbox if the user does not have
        any custom roles assigned. If None the placeholder is removed.

    custom_roles_max_selections : int or None, default None
        The maximum number of custom roles that can be selected in the custom roles multiselectbox.
        If None there is no upper limit.

    custom_roles_help : str or None, default 'The custom roles to associate with the user.'
        The help text to display for the custom roles multiselectbox.
        If None the help text is removed.

    disabled_toggle_label : str, default 'Disabled user'
        The label for the disabled user toggle switch.

    disabled_toggle_help : str or None, default 'If the user should be created as disabled or enabled.'
        The help text to display for the disabled toggle switch. If None the help text is removed.

    Returns
    -------
    user : streamlit_passwordless.db.models.User
        The updated user.

    is_updated : bool
        True if the user was updated and False otherwise.
    """

    banner_container = st.empty() if banner_container is None else banner_container
    banner_container_mapping = {}

    with st.form(key=ids.UPDATE_USER_FORM, clear_on_submit=clear_on_submit, border=border):
        st.markdown(title)

        username_error_banner = st.empty()
        banner_container_mapping[core.FormField.USERNAME] = username_error_banner

        username = st.text_input(
            label=username_label,
            value=user.username,
            placeholder=username_placeholder,
            max_chars=username_max_length,
            help=username_help,
            key=ids.UPDATE_USER_FORM_USERNAME_TEXT_INPUT,
        )

        if with_displayname:
            displayname = st.text_input(
                label=displayname_label,
                value=user.displayname,
                placeholder=displayname_placeholder,
                max_chars=displayname_max_length,
                help=displayname_help,
                key=ids.UPDATE_USER_FORM_DISPLAYNAME_TEXT_INPUT,
            )
        else:
            displayname = None

        if with_ad_username:
            ad_username = st.text_input(
                label=ad_username_label,
                value=user.ad_username,
                placeholder=ad_username_placeholder,
                max_chars=ad_username_max_length,
                help=ad_username_help,
                key=ids.UPDATE_USER_FORM_AD_USERNAME_TEXT_INPUT,
            )
        else:
            ad_username = None

        if with_role:
            if roles is None:
                db_roles, error_msg = core.get_all_roles_from_database(session=db_session)
                if error_msg:
                    core.display_banner_message(
                        message=error_msg,
                        message_type=core.BannerMessageType.ERROR,
                        container=st.empty(),
                    )
            else:
                # Load the cached roles into the current session without a database lookup.
                db_roles = tuple(db_session.merge(r, load=False) for r in roles)

            role = st.selectbox(
                label=role_label,
                options=db_roles if db_roles else tuple(),
                index=db_roles.index(user.role) if roles else 0,  # Role of the current user.
                placeholder=role_placeholder,
                format_func=lambda r: r.name,
                help=role_help,
                key=ids.UPDATE_USER_FORM_ROLE_SELECTBOX,
            )
            role_id = role.role_id
        else:
            role_id = 1

        if with_custom_roles:
            if custom_roles is None:
                st.write(f'Session loading custom roles : {db_session}')
                db_custom_roles, error_msg = core.get_all_custom_roles_from_database(
                    session=db_session
                )
                if error_msg:
                    core.display_banner_message(
                        message=error_msg,
                        message_type=core.BannerMessageType.ERROR,
                        container=st.empty(),
                    )
            else:
                db_custom_roles = tuple(db_session.merge(r, load=False) for r in custom_roles)

            # Widgets return a copy of the selected values.
            # Accessing the selected custom roles from the session state returns the same objects
            # as specified in the `options` parameter. This is important because if copies of
            # custom roles that already exist in the database session are assigned to the user
            # SQLAlchemy will raise an exception.
            st.multiselect(
                label=custom_roles_label,
                options=db_custom_roles,
                default=[role for role in user.custom_roles.values()],
                max_selections=custom_roles_max_selections,
                placeholder=custom_roles_placeholder,
                format_func=lambda r: r.name,
                help=custom_roles_help,
                key=ids.UPDATE_USER_FORM_CUSTOM_ROLES_MULTISELECTBOX,
            )

        if with_disabled_toggle:
            disabled = st.toggle(
                label=disabled_toggle_label,
                value=user.disabled,
                help=disabled_toggle_help,
                key=ids.UPDATE_USER_FORM_DISABLED_TOGGLE,
            )
        else:
            disabled = False

        clicked = st.form_submit_button(
            label=submit_button_label,
            type=submit_button_type,
            on_click=_validate_form,
            kwargs={'db_session': db_session, 'current_username': user.username},
        )

        if not clicked:
            return user, False

        if not st.session_state.get(config.SK_UPDATE_USER_FORM_IS_VALID):
            validation_error_key = config.SK_UPDATE_USER_FORM_VALIDATION_ERRORS
            core.process_form_validation_errors(
                validation_errors=st.session_state[validation_error_key],
                banner_container_mapping=banner_container_mapping,  # type: ignore
                default_banner_container=banner_container,
            )
            st.session_state[validation_error_key] = {}

            return user, False

    if updated_by_user_id is None:
        signed_in_user = config.get_current_user()
        updated_by = signed_in_user.user_id if signed_in_user else None
    else:
        updated_by = updated_by_user_id

    is_updated = _updated_user(
        user=user,
        username=username,
        with_displayname=with_displayname,
        displayname=displayname,
        with_ad_username=with_ad_username,
        ad_username=ad_username,
        with_role=with_role,
        role_id=role_id,
        with_custom_roles=with_custom_roles,
        custom_roles=st.session_state.get(
            ids.UPDATE_USER_FORM_CUSTOM_ROLES_MULTISELECTBOX, tuple()
        ),
        with_disabled=with_disabled_toggle,
        disabled=disabled,
        updated_by_user_id=updated_by,
    )

    if is_updated:
        success, error_msg = core.update_user_in_database(session=db_session, user=user)
        if not success:
            core.display_banner_message(
                message=error_msg,
                message_type=core.BannerMessageType.ERROR,
                container=banner_container,
            )
            return user, False

        msg = f'Successfully updated user: {user.username}!'
        core.display_banner_message(
            message=msg, message_type=core.BannerMessageType.SUCCESS, container=banner_container
        )
    else:
        msg = f'Nothing has changed on user: {user.username}!'
        core.display_banner_message(
            message=msg, message_type=core.BannerMessageType.WARNING, container=banner_container
        )

    return user, is_updated

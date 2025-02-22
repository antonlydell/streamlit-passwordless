r"""The create user form component and its callback functions."""

# Standard library
import logging
from typing import Sequence

# Third party
import streamlit as st

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import models
from streamlit_passwordless.common import get_current_datetime

from . import config, core, ids

logger = logging.getLogger(__name__)


def _validate_form(db_session: db.Session, email_is_username: bool) -> None:
    r"""Validate the input fields of the create user form.

    Updates the following session state keys:
    - `streamlit_passwordless.SK_CREATE_USER_FORM_IS_VALID` :
        True if the form validation passed and False otherwise.

    - `streamlit_passwordless.SK_CREATE_USER_FORM_VALIDATION_ERRORS` :
        A dictionary mapping of the user form field name to its error message.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    email_is_username : bool
        If True the username is the email address of the user and if False
        the username is distinct from an optional email address of the user.
    """

    form_is_valid = True
    validation_errors = {}

    validation_error_field = core.FormField.USERNAME
    if username := st.session_state[ids.CREATE_USER_FORM_USERNAME_TEXT_INPUT]:
        db_user, error_msg = core.get_user_from_database(
            session=db_session, username=username.strip().casefold()
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

    if email_is_username:
        email = username
        validation_error_field = core.FormField.USERNAME
    else:
        email = st.session_state.get(ids.CREATE_USER_FORM_EMAIL_TEXT_INPUT)
        validation_error_field = core.FormField.EMAIL

    if email:
        db_email, error_msg = core.get_email_from_database(
            session=db_session, email=email.strip().casefold()
        )
        if error_msg:  # DatabaseError
            form_is_valid = False
            validation_errors[validation_error_field] = error_msg
        elif db_email is not None:
            form_is_valid = False
            validation_errors[validation_error_field] = (
                f'{"User" if email_is_username else "Email"} {email} already exists!'
            )
        else:
            pass

    st.session_state[config.SK_CREATE_USER_FORM_VALIDATION_ERRORS] = validation_errors
    st.session_state[config.SK_CREATE_USER_FORM_IS_VALID] = form_is_valid


def create_user_form(
    db_session: db.Session,
    with_displayname: bool = True,
    with_ad_username: bool = False,
    with_role: bool = True,
    with_custom_roles: bool = True,
    with_email: bool = True,
    with_disabled_toggle: bool = True,
    email_is_username: bool = False,
    roles: Sequence[models.Role] | None = None,
    custom_roles: Sequence[db.models.CustomRole] | None = None,
    title: str = '#### Create a new user',
    border: bool = True,
    submit_button_label: str = 'Create User',
    submit_button_type: core.ButtonType = 'primary',
    clear_on_submit: bool = False,
    banner_container: core.BannerContainer | None = None,
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
    role_preselected: int | None = 0,
    role_help: str | None = 'The role of the user.',
    custom_roles_label: str = 'Custom Roles',
    custom_roles_placeholder: str = 'Choose a custom role',
    custom_roles_max_selections: int | None = None,
    custom_roles_default_selection: (
        Sequence[db.models.CustomRole] | db.models.CustomRole | None
    ) = None,
    custom_roles_help: str | None = 'The custom roles to associate with the user.',
    email_label: str = 'Email',
    email_max_length: int | None = 50,
    email_placeholder: str | None = 'john.doe@example.com',
    email_help: str | None = 'An email address to associate with the user.',
    disabled_toggle_label: str = 'Disabled User',
    disabled_toggle_default_value: bool = False,
    disabled_toggle_help: str | None = 'If the user should be created as disabled or enabled.',
) -> models.User | None:
    r"""Render the create user form.

    Create a new user in the database without registering a passkey.

    Parameters
    ----------
    db_session : streamlit_passwordless.db.Session
        An active database session.

    with_displayname : bool, default True
        If True the displayname field is added to the form to enable to
        enter a displayname for the user.

    with_ad_username : bool, default False
        If True the ad_username field is added to the form to enable to
        enter the active directory username for the user.

    with_role : bool, default True
        If True the role selectbox is added to the form to enable to set
        the desired role for the new user.

    with_custom_roles : bool, default False
        If True the custom roles multiselectbox is added to the form, given that the
        `custom_roles` parameter is specified, to enable to set the desired custom roles
        for the new user.

    with_email : bool, default False
        If True the email field is added to the form to enable to
        enter an email address to associate with the user.

    with_disabled_toggle : bool, default True
        If True the disabled user toggle switch will be added to the form, which enables
        creating a new user as disabled or enabled. If False a new user will be created as enabled.

    email_is_username : bool, default False
        If True the username field will prompt to enter an email address, which will be used
        as the username and be added as an email address of the user.

    roles : Sequence[streamlit_passwordless.Role] or None, default None
        The available roles that can be assigned to the user. If None the
        default roles of Streamlit Passwordless will be used.

    custom_roles : Sequence[streamlit_passwordless.db.models.CustomRole] or None, default None
        The available custom roles that can be assigned to the user. If None the defined
        custom roles in the database will be loaded and made available for selection.

    title : str, default '#### Create a new user'
        The title of the create user form. Markdown is supported.

    border : bool, default True
        If True a border will be rendered around the form.

    submit_button_label : str, default 'Create User'
        The label of the form submit button.

    submit_button_type : Literal['primary', 'secondary'], default 'primary'
        The styling of the submit button. Emulates the `type` parameter of :func:`streamlit.button`.

    clear_on_submit : bool, default False
        If True the form fields will be cleared when the submit form button is clicked.

    banner_container : streamlit_passwordless.BannerContainer or None, default None
        A container produced by :func:`streamlit.empty`, in which error or success messages about
        the create user process will be displayed. Useful to make the banner appear at the desired
        location on a page. If None the banner will be displayed right above the form.

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

    role_preselected : int or None, default 0
        The index value of `roles` that will be used to extract the default selected role of
        the role selectbox. If None no role will be selected by default on first render.

    role_help: str or None, default 'The role of the user.'
        The help text to display for the role selectbox. If None the help text is removed.

    custom_roles_label : str, default 'Custom Roles',
        The label of the custom roles multiselectbox.

    custom_roles_placeholder : str, default 'Choose a custom role'
        The placeholder of the custom roles multiselectbox if no custom roles are preselected.
        If None the placeholder is removed.

    custom_roles_max_selections : int or None, default None
        The maximum number of custom roles that can be selected in the custom roles multiselectbox.
        If None there is no upper limit.

    custom_roles_default_selection : Sequence[streamlit_passwordless.db.models.CustomRole] or streamlit_passwordless.models.db.CustomRole or None, default None
        The custom roles that will be preselected in the the custom roles mulitselectbox.
        If None no custom roles will be preselected on first render.

    custom_roles_help : str or None, default 'The custom roles to associate with the user.'
        The help text to display for the custom roles multiselectbox.
        If None the help text is removed.

    email_label : str, default 'Email'
        The label of the email field.

    email_max_length : int or None, default 50
        The maximum allowed number of characters of the email field.
        If None the upper limit is removed.

    email_placeholder : str or None, default 'john.doe@example.com'
        The placeholder of the email field. If None the placeholder is removed.

    email_help : str or None, default 'An email address to associate with the user.'
        The help text to display for the email field. If None the help text is removed.

    disabled_toggle_label : str, default 'Disabled user'
        The label for the disabled user toggle switch.

    disabled_toggle_default_value : bool, default False
        The default value of the disabled user toggle switch. True means a user will be created
        as disabled and False as enabled.

    disabled_toggle_help : str or None, default 'If the user should be created as disabled or enabled.'
        The help text to display for the disabled toggle switch. If None the help text is removed.

    Returns
    -------
    user : streamlit_passwordless.User or None
        The created user. None is returned if a user could not be created.
    """

    banner_container = st.empty() if banner_container is None else banner_container
    banner_container_mapping = {}

    with st.form(key=ids.CREATE_USER_FORM, clear_on_submit=clear_on_submit, border=border):
        st.markdown(title)

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
            help=username_help,
            key=ids.CREATE_USER_FORM_USERNAME_TEXT_INPUT,
        )

        if with_displayname:
            displayname = st.text_input(
                label=displayname_label,
                placeholder=displayname_placeholder,
                max_chars=displayname_max_length,
                help=displayname_help,
                key=ids.CREATE_USER_FORM_DISPLAYNAME_TEXT_INPUT,
            )
        else:
            displayname = None

        if with_ad_username:
            ad_username = st.text_input(
                label=ad_username_label,
                placeholder=ad_username_placeholder,
                max_chars=ad_username_max_length,
                help=ad_username_help,
                key=ids.CREATE_USER_FORM_AD_USERNAME_TEXT_INPUT,
            )
        else:
            ad_username = None

        if with_role:
            if roles is None:
                roles = (models.ViewerRole, models.UserRole, models.SuperUserRole, models.AdminRole)
                role_preselected = 1
            role = st.selectbox(
                label=role_label,
                options=roles,
                index=role_preselected,
                placeholder=role_placeholder,
                format_func=lambda r: r.name,
                help=role_help,
                key=ids.CREATE_USER_FORM_ROLE_SELECTBOX,
            )
        else:
            role = models.UserRole

        if with_custom_roles:
            if custom_roles is None:
                db_custom_roles = db.get_all_custom_roles(session=db_session)
            else:
                db_custom_roles = custom_roles
            selected_custom_roles: Sequence[db.models.CustomRole] = st.multiselect(
                label=custom_roles_label,
                options=db_custom_roles,
                default=custom_roles_default_selection,
                max_selections=custom_roles_max_selections,
                placeholder=custom_roles_placeholder,
                format_func=lambda r: r.name,
                help=custom_roles_help,
                key=ids.CREATE_USER_FORM_CUSTOM_ROLES_MULTISELECTBOX,
            )
        if with_email:
            if not email_is_username:
                email_error_banner = st.empty()
                banner_container_mapping[core.FormField.EMAIL] = email_error_banner
                email = st.text_input(
                    label=email_label,
                    placeholder=email_placeholder,
                    max_chars=email_max_length,
                    help=email_help,
                    key=ids.CREATE_USER_FORM_EMAIL_TEXT_INPUT,
                )
            else:
                email = username
        else:
            email = None

        if with_disabled_toggle:
            disabled = st.toggle(
                label=disabled_toggle_label,
                value=disabled_toggle_default_value,
                help=disabled_toggle_help,
                key=ids.CREATE_USER_FORM_DISABLED_TOGGLE,
            )
        else:
            disabled = False

        clicked = st.form_submit_button(
            label=submit_button_label,
            type=submit_button_type,
            on_click=_validate_form,
            kwargs={'db_session': db_session, 'email_is_username': email_is_username},
        )

        if not clicked:
            return None

        if not st.session_state.get(config.SK_CREATE_USER_FORM_IS_VALID):
            validation_error_key = config.SK_CREATE_USER_FORM_VALIDATION_ERRORS
            core.process_form_validation_errors(
                validation_errors=st.session_state[validation_error_key],
                banner_container_mapping=banner_container_mapping,  # type: ignore
                default_banner_container=banner_container,
            )
            st.session_state[validation_error_key] = {}

            return None

    user = models.User(
        username=username.strip(),
        ad_username=None if ad_username is None else ad_username.strip(),
        displayname=None if displayname is None else displayname.strip(),
        disabled=disabled,
        disabled_timestamp=get_current_datetime() if disabled else None,
        role=models.UserRole if role is None else role,
        emails=[models.Email(email=email.strip().casefold(), rank=1)] if email else None,
        custom_roles={m.name: models.CustomRole.model_validate(m) for m in selected_custom_roles},
    )
    success, error_msg = core.create_user_in_database(session=db_session, user=user)
    if not success:
        core.display_banner_message(
            message=error_msg, message_type=core.BannerMessageType.ERROR, container=banner_container
        )
        return None

    msg = f'Successfully created user: {user.username}!'
    logger.info(msg)
    core.display_banner_message(
        message=msg, message_type=core.BannerMessageType.SUCCESS, container=banner_container
    )

    return user

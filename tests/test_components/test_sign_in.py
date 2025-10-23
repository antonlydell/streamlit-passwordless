r"""Unit tests for the sign in related components."""

# Standard library
from unittest.mock import Mock

# Third party
import pytest
from sqlalchemy import select
from streamlit.testing.v1 import AppTest

# Local
from streamlit_passwordless import ICON_ERROR, SK_USER
from streamlit_passwordless import database as db
from streamlit_passwordless.components.ids import (
    BP_SIGN_IN_BUTTON,
    BP_SIGN_IN_FORM_SUBMIT_BUTTON,
)
from streamlit_passwordless.database import models as db_models
from streamlit_passwordless.models import AdminRole, UserSignIn
from tests.config import test_app_config

# =============================================================================================
# Tests
# =============================================================================================


@pytest.mark.usefixtures('mocked_bwp_sign_in_button_success')
class TestBitwardenSignInPositive:
    r"""Positive tests for the sign in components."""

    @pytest.mark.parametrize(
        ('key', 'user_return_value', 'success_return_value', 'defer_role_description'),
        [
            pytest.param(
                BP_SIGN_IN_FORM_SUBMIT_BUTTON,
                'user_sign_in_form',
                'success_sign_in_form',
                True,
                id='bitwarden_sign_in_form defer role description',
            ),
            pytest.param(
                BP_SIGN_IN_FORM_SUBMIT_BUTTON,
                'user_sign_in_form',
                'success_sign_in_form',
                False,
                id='bitwarden_sign_in_form include role description',
            ),
            pytest.param(
                BP_SIGN_IN_BUTTON,
                'user_sign_in_button',
                'success_sign_in_button',
                True,
                id='bitwarden_sign_in_button defer role description',
            ),
            pytest.param(
                BP_SIGN_IN_BUTTON,
                'user_sign_in_button',
                'success_sign_in_button',
                False,
                id='bitwarden_sign_in_button include role description',
            ),
        ],
    )
    def test_load_role(
        self,
        key: str,
        user_return_value: str,
        success_return_value: str,
        defer_role_description: bool,
        sqlite_db_with_user: tuple[db.Session, db.SessionFactory, db_models.User],
        bwp_client_with_successful_sign_in: tuple[Mock, UserSignIn],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign in and load the role of the signed in user."""

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_db_with_user
        role_exp = user_exp.role
        client, user_sign_in_exp = bwp_client_with_successful_sign_in

        # One user sign in already exists in the database.
        query_user_sign_in = (
            select(db_models.UserSignIn)
            .where(db_models.UserSignIn.user_id == user_exp.user_id)
            .order_by(db_models.UserSignIn.user_sign_in_id.desc())
            .limit(1)
        )

        app = app_components
        app.session_state['client'] = client
        app.session_state['session_factory'] = session_factory
        app.session_state['sign_in_params'] = {
            'load_custom_roles': False,
            'load_emails': False,
            'defer_role_description': defer_role_description,
        }

        # Exercise
        # ===========================================================
        app.run()
        app.button(key=key).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'

        # User
        user = app.session_state[user_return_value]
        success = app.session_state[success_return_value]

        assert user is not None, 'The signed in user was not returned from the component!'
        assert success is True, 'The success state of signed in user was False!'

        user_session_state = app.session_state[SK_USER]
        assert user is user_session_state, (
            'The returned user is not the same as the user in the session state!'
        )

        user_attributes_to_verify = (
            ('user_id', user_exp.user_id),
            ('username', user_exp.username),
            ('ad_username', user_exp.ad_username),
            ('displayname', user_exp.displayname),
            ('verified_at', user_exp.verified_at),
            ('disabled', user_exp.disabled),
            ('disabled_at', user_exp.disabled_at),
        )
        for attr, exp_value in user_attributes_to_verify:
            assert getattr(user, attr) == exp_value, f'user.{attr} is incorrect!'

        # Role
        role = user.role
        role_attributes_to_verify = (
            ('role_id', role_exp.role_id),
            ('name', role_exp.name),
            ('rank', role_exp.rank),
            ('description', None if defer_role_description else role_exp.description),
        )
        for attr, exp_value in role_attributes_to_verify:  # type: ignore[assignment]
            assert getattr(role, attr) == exp_value, f'role.{attr} is incorrect!'

        # CustomRole
        assert user.custom_roles == {}, 'Custom roles were loaded!'

        # Email
        assert user.emails == [], 'Emails were loaded!'

        # UserSignIn
        with session_factory() as new_session:
            db_user_sign_in = new_session.scalars(query_user_sign_in).one()

        user_sign_in = user.sign_in
        assert user_sign_in is not None, 'user.sign_in is None!'

        user_sign_in_attributes_to_verify = (
            ('user_sign_in_id', 2),
            ('user_id', user_sign_in_exp.user_id),
            ('sign_in_timestamp', user_sign_in_exp.sign_in_timestamp),
            ('success', user_sign_in_exp.success),
            ('origin', user_sign_in_exp.origin),
            ('device', user_sign_in_exp.device),
            ('country', user_sign_in_exp.country),
            ('credential_nickname', user_sign_in_exp.credential_nickname),
            ('credential_id', user_sign_in_exp.credential_id),
            ('sign_in_type', user_sign_in_exp.sign_in_type),
            ('rp_id', user_sign_in_exp.rp_id),
        )
        for attr, exp_value in user_sign_in_attributes_to_verify:  # type: ignore[assignment]
            assert getattr(db_user_sign_in, attr) == exp_value, (
                f'db_user_sign_in.{attr} is incorrect!'
            )
            exp_value = None if attr == 'user_sign_in_id' else exp_value
            assert getattr(user_sign_in, attr) == exp_value, f'user_sign_in.{attr} is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        ('key', 'user_return_value', 'success_return_value', 'defer_role_description'),
        [
            pytest.param(
                BP_SIGN_IN_FORM_SUBMIT_BUTTON,
                'user_sign_in_form',
                'success_sign_in_form',
                True,
                id='bitwarden_sign_in_form defer role description',
            ),
            pytest.param(
                BP_SIGN_IN_FORM_SUBMIT_BUTTON,
                'user_sign_in_form',
                'success_sign_in_form',
                False,
                id='bitwarden_sign_in_form include role description',
            ),
            pytest.param(
                BP_SIGN_IN_BUTTON,
                'user_sign_in_button',
                'success_sign_in_button',
                True,
                id='bitwarden_sign_in_button defer role description',
            ),
            pytest.param(
                BP_SIGN_IN_BUTTON,
                'user_sign_in_button',
                'success_sign_in_button',
                False,
                id='bitwarden_sign_in_button include role description',
            ),
        ],
    )
    def test_load_custom_roles(
        self,
        key: str,
        user_return_value: str,
        success_return_value: str,
        defer_role_description: bool,
        sqlite_db_with_user: tuple[db.Session, db.SessionFactory, db_models.User],
        bwp_client_with_successful_sign_in: tuple[Mock, UserSignIn],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign in and load the custom roles of the signed in user."""

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_db_with_user
        role_exp = user_exp.role
        custom_roles_exp = user_exp.custom_roles
        nr_custom_roles_exp = len(custom_roles_exp)
        client, _ = bwp_client_with_successful_sign_in

        app = app_components
        app.session_state['client'] = client
        app.session_state['session_factory'] = session_factory
        app.session_state['sign_in_params'] = {
            'load_custom_roles': True,
            'load_emails': False,
            'defer_role_description': defer_role_description,
        }

        # Exercise
        # ===========================================================
        app.run()
        app.button(key=key).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'

        # User
        user = app.session_state[user_return_value]
        success = app.session_state[success_return_value]

        assert user is not None, 'The signed in user was not returned from the component!'
        assert success is True, 'The success state of signed in user was False!'

        user_session_state = app.session_state[SK_USER]
        assert user is user_session_state, (
            'The returned user is not the same as the user in the session state!'
        )

        user_attributes_to_verify = (
            ('user_id', user_exp.user_id),
            ('username', user_exp.username),
            ('ad_username', user_exp.ad_username),
            ('displayname', user_exp.displayname),
            ('verified_at', user_exp.verified_at),
            ('disabled', user_exp.disabled),
            ('disabled_at', user_exp.disabled_at),
        )
        for attr, exp_value in user_attributes_to_verify:
            assert getattr(user, attr) == exp_value, f'user.{attr} is incorrect!'

        # Role
        role = user.role
        role_attributes_to_verify = (
            ('role_id', role_exp.role_id),
            ('name', role_exp.name),
            ('rank', role_exp.rank),
            ('description', None if defer_role_description else role_exp.description),
        )
        for attr, exp_value in role_attributes_to_verify:  # type: ignore[assignment]
            assert getattr(role, attr) == exp_value, f'role.{attr} is incorrect!'

        # CustomRole
        assert len(user.custom_roles) == nr_custom_roles_exp, (
            'Incorrect number of custom roles were loaded!'
        )

        for role_id, custom_role in user.custom_roles.items():
            custom_role_exp = custom_roles_exp.get(role_id)

            assert custom_role_exp is not None, (
                f'{custom_role.name} not among the expected custom roles!'
            )

            custom_role_attributes_to_verify = (
                ('role_id', custom_role_exp.role_id),
                ('name', custom_role_exp.name),
                ('rank', custom_role_exp.rank),
                ('description', None if defer_role_description else custom_role_exp.description),
            )
            for attr, exp_value in custom_role_attributes_to_verify:  # type: ignore[assignment]
                assert getattr(custom_role, attr) == exp_value, (
                    f'{custom_role.name} : custom_role.{attr} is incorrect!'
                )

        # Email
        assert user.emails == [], 'Emails were loaded!'

        # UserSignIn
        assert user.sign_in is not None, 'user.sign_in is None!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        ('key', 'user_return_value', 'success_return_value'),
        [
            pytest.param(
                BP_SIGN_IN_FORM_SUBMIT_BUTTON,
                'user_sign_in_form',
                'success_sign_in_form',
                id='bitwarden_sign_in_form',
            ),
            pytest.param(
                BP_SIGN_IN_BUTTON,
                'user_sign_in_button',
                'success_sign_in_button',
                id='bitwarden_sign_in_button',
            ),
        ],
    )
    def test_load_emails(
        self,
        key: str,
        user_return_value: str,
        success_return_value: str,
        sqlite_db_with_user: tuple[db.Session, db.SessionFactory, db_models.User],
        bwp_client_with_successful_sign_in: tuple[Mock, UserSignIn],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign in and load the (non-disabled) emails of the signed in user."""

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_db_with_user
        role_exp = user_exp.role
        email_exp = user_exp.emails[0]  # The primary email
        nr_emails_exp = 1
        client, _ = bwp_client_with_successful_sign_in

        app = app_components
        app.session_state['client'] = client
        app.session_state['session_factory'] = session_factory
        app.session_state['sign_in_params'] = {
            'load_custom_roles': False,
            'load_emails': True,
            'defer_role_description': True,
        }

        # Exercise
        # ===========================================================
        app.run()
        app.button(key=key).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'

        # User
        user = app.session_state[user_return_value]
        success = app.session_state[success_return_value]

        assert user is not None, 'The signed in user was not returned from the component!'
        assert success is True, 'The success state of signed in user was False!'

        user_session_state = app.session_state[SK_USER]
        assert user is user_session_state, (
            'The returned user is not the same as the user in the session state!'
        )

        user_attributes_to_verify = (
            ('user_id', user_exp.user_id),
            ('username', user_exp.username),
            ('ad_username', user_exp.ad_username),
            ('displayname', user_exp.displayname),
            ('verified_at', user_exp.verified_at),
            ('disabled', user_exp.disabled),
            ('disabled_at', user_exp.disabled_at),
        )
        for attr, exp_value in user_attributes_to_verify:
            assert getattr(user, attr) == exp_value, f'user.{attr} is incorrect!'

        # Role
        role = user.role
        role_attributes_to_verify = (
            ('role_id', role_exp.role_id),
            ('name', role_exp.name),
            ('rank', role_exp.rank),
            ('description', None),
        )
        for attr, exp_value in role_attributes_to_verify:  # type: ignore[assignment]
            assert getattr(role, attr) == exp_value, f'role.{attr} is incorrect!'

        # CustomRole
        assert user.custom_roles == {}, 'Custom roles were loaded!'

        # Emails
        emails = user.emails
        assert len(emails) == nr_emails_exp, 'More emails than the primary email were loaded!'

        email = emails[0]
        email_attributes_to_verify = (
            ('email_id', email_exp.email_id),
            ('email', email_exp.email),
            ('rank', email_exp.rank),
            ('verified', email_exp.verified),
            ('verified_at', email_exp.verified_at),
            ('disabled', email_exp.disabled),
            ('disabled_at', email_exp.disabled_at),
        )
        for attr, exp_value in email_attributes_to_verify:  # type: ignore[assignment]
            assert getattr(email, attr) == exp_value, f'{email.email} : email.{attr} is incorrect!'

        # UserSignIn
        assert user.sign_in is not None, 'user.sign_in is None!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'key',
        [
            pytest.param(BP_SIGN_IN_FORM_SUBMIT_BUTTON, id='bitwarden_sign_in_form'),
            pytest.param(BP_SIGN_IN_BUTTON, id='bitwarden_sign_in_button'),
        ],
    )
    def test_redirect_to_authorized_page(
        self,
        key: str,
        sqlite_db_with_user: tuple[db.Session, db.SessionFactory, db_models.User],
        bwp_client_with_successful_sign_in: tuple[Mock, UserSignIn],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign in and redirect to a page the user is authorized to access.

        After successful sign in the user will be redirected to the home page, which
        requires that the user is signed in.
        """

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_db_with_user
        client, _ = bwp_client_with_successful_sign_in

        app = app_components
        app.session_state['client'] = client
        app.session_state['session_factory'] = session_factory
        app.session_state['sign_in_params'] = {'redirect': test_app_config.home_page.path}

        # Exercise
        # ===========================================================
        app.run()
        app.button(key=key).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'
        assert app.title[0].value == test_app_config.home_page.title, (
            'The title of the page after redirect is incorrect!'
        )

        # Clean up - None
        # ===========================================================


@pytest.mark.usefixtures('mocked_bwp_sign_in_button_success')
class TestBitwardenSignInNegative:
    r"""Negative tests for the sign in components."""

    @pytest.mark.parametrize(
        ('key', 'user_return_value', 'success_return_value'),
        [
            pytest.param(
                BP_SIGN_IN_FORM_SUBMIT_BUTTON,
                'user_sign_in_form',
                'success_sign_in_form',
                id='bitwarden_sign_in_form',
            ),
            pytest.param(
                BP_SIGN_IN_BUTTON,
                'user_sign_in_button',
                'success_sign_in_button',
                id='bitwarden_sign_in_button',
            ),
        ],
    )
    def test_unauthorized_sign_in(
        self,
        key: str,
        user_return_value: str,
        success_return_value: str,
        sqlite_db_with_user: tuple[db.Session, db.SessionFactory, db_models.User],
        bwp_client_with_successful_sign_in: tuple[Mock, UserSignIn],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign in a user carrying a role with an insufficient rank.

        An error banner should be displayed stating that the user is not authorized
        to sign in. The user sign in entry should not be saved to the database.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_db_with_user
        role_exp = user_exp.role
        client, _ = bwp_client_with_successful_sign_in

        query_user_sign_in = select(db_models.UserSignIn).where(
            db_models.UserSignIn.user_id == user_exp.user_id
        )
        nr_user_sign_ins_exp = 1  # One user sign in already exists in the database.

        app = app_components
        app.session_state['client'] = client
        app.session_state['session_factory'] = session_factory
        app.session_state['sign_in_params'] = {'role': AdminRole}

        # Exercise
        # ===========================================================
        app.run()
        app.button(key=key).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'

        user = app.session_state[user_return_value]
        success = app.session_state[success_return_value]

        assert user is not None, 'The signed in user was not returned from the component!'
        assert success is False, 'The success state of signed in user was True!'

        # Error banner
        error_banner = app.error[0]
        assert error_banner.value == f'User {user.username} is not authorized to sign in!', (
            'Incorrect error banner message!'
        )
        assert error_banner.icon == ICON_ERROR, 'Incorrect icon in error banner!'

        # User
        user_from_session_state = app.session_state[SK_USER]
        assert user is user_from_session_state, (
            'The returned user is not the same as the user in the session state!'
        )

        user_attributes_to_verify = (
            ('user_id', user_exp.user_id),
            ('username', user_exp.username),
            ('ad_username', user_exp.ad_username),
            ('displayname', user_exp.displayname),
            ('verified_at', user_exp.verified_at),
            ('disabled', user_exp.disabled),
            ('disabled_at', user_exp.disabled_at),
        )
        for attr, exp_value in user_attributes_to_verify:
            assert getattr(user, attr) == exp_value, f'user.{attr} is incorrect!'

        # Role
        role = user.role
        role_attributes_to_verify = (
            ('role_id', role_exp.role_id),
            ('name', role_exp.name),
            ('rank', role_exp.rank),
            ('description', None),
        )
        for attr, exp_value in role_attributes_to_verify:  # type: ignore[assignment]
            assert getattr(role, attr) == exp_value, f'role.{attr} is incorrect!'

        # CustomRole
        assert user.custom_roles == {}, 'Custom roles were loaded!'

        # Email
        assert user.emails == [], 'Emails were loaded!'

        # UserSignIn
        with session_factory() as new_session:
            db_user_sign_in = new_session.scalars(query_user_sign_in).all()

        assert len(db_user_sign_in) == nr_user_sign_ins_exp, (
            'Incorrect number of user sign in entries in the database!'
        )
        assert user.sign_in is None, 'user.sign_in is not None!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'key',
        [
            pytest.param(BP_SIGN_IN_FORM_SUBMIT_BUTTON, id='bitwarden_sign_in_form'),
            pytest.param(BP_SIGN_IN_BUTTON, id='bitwarden_sign_in_button'),
        ],
    )
    def test_redirect_to_unauthorized_page(
        self,
        key: str,
        sqlite_db_with_user: tuple[db.Session, db.SessionFactory, db_models.User],
        bwp_client_with_successful_sign_in: tuple[Mock, UserSignIn],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign in and redirect to a page the user is not authorized to access.

        The test user has a role of SuperUser and should not be able to access the admin page.
        """

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_db_with_user
        client, _ = bwp_client_with_successful_sign_in

        app = app_components
        app.session_state['client'] = client
        app.session_state['session_factory'] = session_factory
        app.session_state['sign_in_params'] = {'redirect': test_app_config.admin_page.path}

        # Exercise
        # ===========================================================
        app.run()
        app.button(key=key).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'
        assert app.title[0].value == test_app_config.sign_in_page.title, (
            'The title of the page is incorrect!'
        )

        # Clean up - None
        # ===========================================================

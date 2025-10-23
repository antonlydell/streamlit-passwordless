r"""Unit tests for the sign out related components."""

# Standard library
from unittest.mock import Mock

# Third party
import pytest
from streamlit.testing.v1 import AppTest

# Local
from streamlit_passwordless import SK_USER, SK_USER_SIGN_IN, User
from streamlit_passwordless.components.ids import KEY_SIGN_OUT_BUTTON
from streamlit_passwordless.database import Session, SessionFactory
from streamlit_passwordless.database import models as db_models
from tests.config import ModelData, test_app_config

# =============================================================================================
# Tests
# =============================================================================================


class TestBitwardenSignOutButton:
    r"""Tests for the component `sign_out_button`."""

    @pytest.mark.usefixtures('mocked_bwp_sign_in_button_success')
    def test_sign_out_user(
        self,
        empty_sqlite_in_memory_database: tuple[Session, SessionFactory],
        user_1_with_2_emails_and_successful_signin: tuple[User, db_models.User, ModelData],
        app_components: AppTest,
    ) -> None:
        r"""Test to sign out a user from the app.

        After successful sign out the user should not be able to access the home page,
        which requires that the user is signed in.
        """

        # Setup
        # ===========================================================
        _, session_factory = empty_sqlite_in_memory_database
        user, _, _ = user_1_with_2_emails_and_successful_signin

        assert user.sign_in is not None, 'user.sign_in is None during test setup!'

        app = app_components
        app.session_state['client'] = Mock()
        app.session_state['session_factory'] = session_factory
        app.session_state[SK_USER] = user

        # Exercise
        # ===========================================================
        app.run()
        app.switch_page(test_app_config.home_page.path).run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'
        assert app.title[0].value == test_app_config.home_page.title, (
            'The title of the expected home page is incorrect!'
        )

        # Exercise
        # ===========================================================
        app.sidebar.button(key=KEY_SIGN_OUT_BUTTON).click().run()

        # Verify
        # ===========================================================
        assert not app.exception, 'An exception occurred during app execution!'
        assert app.title[0].value == test_app_config.sign_in_page.title, (
            'The title of the page after sign out is incorrect!'
        )

        assert app.session_state[SK_USER_SIGN_IN] is None, (
            'UserSignIn in session state is not None after sign out!'
        )
        assert user.sign_in is None, 'user.sign_in is not None after sign out!'

        # Clean up - None
        # ===========================================================

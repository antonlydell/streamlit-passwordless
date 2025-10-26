r"""Unit tests for the auth module of Streamlit Passwordless."""

# Third party
import pytest

# Local
import streamlit_passwordless.auth
from streamlit_passwordless import User, authenticated
from streamlit_passwordless.database.models import User as DbUser
from tests.config import ModelData


class TestAuthenticated:
    r"""Tests for the function streamlit_passwordless.authenticated`."""

    def test_user_is_none(self) -> None:
        r"""The user model in the session state is None, i.e. a user has not signed in yet."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        auth, user = authenticated()

        # Verify
        # ===========================================================
        assert auth is False, 'auth is True'
        assert user is None, 'user is not None!'

        # Clean up - None
        # ===========================================================

    def test_user_is_signed_in_get_user_from_session_state(
        self,
        monkeypatch: pytest.MonkeyPatch,
        user_1_with_2_emails_and_successful_signin: tuple[User, DbUser, ModelData],
    ) -> None:
        r"""The user is signed in and should be marked as authenticated."""

        # Setup
        # ===========================================================
        user_exp, _, _ = user_1_with_2_emails_and_successful_signin
        monkeypatch.setattr(streamlit_passwordless.auth, 'get_current_user', lambda: user_exp)

        # Exercise
        # ===========================================================
        auth, user = authenticated()

        # Verify
        # ===========================================================
        assert auth is True, 'auth is False'
        assert user is user_exp, 'user is not the expected user!'

        # Clean up - None
        # ===========================================================

    def test_user_is_signed_in_pass_user_as_argument(
        self, user_1_with_2_emails_and_successful_signin: tuple[User, DbUser, ModelData]
    ) -> None:
        r"""The user is signed in and should be marked as authenticated."""

        # Setup
        # ===========================================================
        user_exp, _, _ = user_1_with_2_emails_and_successful_signin

        # Exercise
        # ===========================================================
        auth, user = authenticated(user=user_exp)

        # Verify
        # ===========================================================
        assert auth is True, 'auth is False'
        assert user is user_exp, 'user is not the expected user!'

        # Clean up - None
        # ===========================================================

    def test_user_is_not_signed_in_get_user_from_session_state(
        self,
        monkeypatch: pytest.MonkeyPatch,
        user_1_with_unsuccessful_signin: tuple[User, DbUser, ModelData],
    ) -> None:
        r"""The user is not signed in and should not be marked as authenticated."""

        # Setup
        # ===========================================================
        user_exp, _, _ = user_1_with_unsuccessful_signin
        monkeypatch.setattr(streamlit_passwordless.auth, 'get_current_user', lambda: user_exp)

        # Exercise
        # ===========================================================
        auth, user = authenticated()

        # Verify
        # ===========================================================
        assert auth is False, 'auth is True'
        assert user is user_exp, 'user is not the expected user!'

        # Clean up - None
        # ===========================================================

    def test_user_is_not_signed_in_pass_user_as_argument(
        self, user_1_with_unsuccessful_signin: tuple[User, DbUser, ModelData]
    ) -> None:
        r"""The user is not signed in and should not be marked as authenticated."""

        # Setup
        # ===========================================================
        user_exp, _, _ = user_1_with_unsuccessful_signin

        # Exercise
        # ===========================================================
        auth, user = authenticated(user=user_exp)

        # Verify
        # ===========================================================
        assert auth is False, 'auth is True'
        assert user is user_exp, 'user is not the expected user!'

        # Clean up - None
        # ===========================================================

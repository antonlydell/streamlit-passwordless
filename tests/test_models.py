r"""Unit tests for the models' module."""

# Standard library
from typing import Sequence

# Third party
import pytest

# Local
from streamlit_passwordless import exceptions, models


# =============================================================================================
# Tests
# =============================================================================================


class TestUser:
    r"""Tests for the `User` model."""

    def test_init_with_defaults(self, mocked_user_id: str) -> None:
        r"""Test to initialize an instance of `User` with all default values."""

        # Setup
        # ===========================================================
        data = {
            'username': 'm.shadows',
            'user_id': mocked_user_id,
            'email': None,
            'displayname': None,
            'aliases': None,
        }

        # Exercise
        # ===========================================================
        user = models.User(**data)

        # Verify
        # ===========================================================
        assert user.dict() == data

        # Clean up - None
        # ===========================================================

    def test_init_supply_all_parameters(self) -> None:
        r"""Test supply values for all parameters of the `User` model."""

        # Setup
        # ===========================================================
        data = {
            'username': 'm.shadows',
            'user_id': 'some-user-id',
            'email': 'm.shadows@ax7.com',
            'displayname': 'M Shadows',
            'aliases': ('Matt', 'Shadows'),
        }

        # Exercise
        # ===========================================================
        user = models.User(**data)

        # Verify
        # ===========================================================
        assert user.dict() == data

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'aliases, aliases_exp',
        (
            pytest.param(None, None, id='None'),
            pytest.param(('Matt', 'Shadows'), ('Matt', 'Shadows'), id="('Matt', 'Shadows')"),
            pytest.param(['Matt', 'Shadows'], ('Matt', 'Shadows'), id="['Matt', 'Shadows']"),
            pytest.param('Matt;Shadows', ('Matt', 'Shadows'), id='Matt;Shadows;'),
            pytest.param('Matt', ('Matt',), id='str'),
            pytest.param('Matt;', ('Matt',), id='Matt;'),
        ),
    )
    def test_aliases(
        self, aliases: str | Sequence[str], aliases_exp: tuple[str, ...] | None
    ) -> None:
        r"""Test to supply different types of aliases."""

        # Setup
        # ===========================================================
        username = 'm.shadows'

        # Exercise
        # ===========================================================
        user = models.User(username=username, aliases=aliases)

        # Verify
        # ===========================================================
        assert user.aliases == aliases_exp

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_username(self) -> None:
        r"""Test supply an invalid username.

        `exceptions.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            models.User(username=None)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'username' in error_msg, 'username not in error message!'

        # Clean up - None
        # ===========================================================

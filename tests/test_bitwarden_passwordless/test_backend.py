r"""Unit tests for the backend module of the bitwarden_passwordless library."""

# Standard library
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

# Third party
import pytest
from passwordless import VerifiedUser
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessVerifiedUser

# =============================================================================================
# Tests
# =============================================================================================


class TestBitwardenPasswordlessVerifiedUser:
    r"""Tests for the `BitwardenPasswordlessVerifiedUser` model."""

    def test__init__(self) -> None:
        r"""Test to initialize the model without errors."""

        # Setup
        # ===========================================================
        data = {
            'success': True,
            'user_id': 'user_id',
            'sign_in_timestamp': '2024-04-27 18:23:52+02:00',
            'origin': 'https://ax7.com',
            'device': 'My device',
            'country': 'SE',
            'credential_nickname': 'credential_nickname',
            'credential_id': 'credential_id',
            'expires_at': '2024-04-27 19:23:52',
            'token_id': 'token_id',
            'type': 'type',
            'rp_id': 'rp_id',
        }

        data_exp = data.copy()
        data_exp['origin'] = AnyHttpUrl(data['origin'])  # type: ignore
        data_exp['sign_in_timestamp'] = datetime(2024, 4, 27, 18, 23, 52, tzinfo=ZoneInfo('CET'))
        data_exp['expires_at'] = datetime(2024, 4, 27, 19, 23, 52)

        # Exercise
        # ===========================================================
        verified_user = BitwardenPasswordlessVerifiedUser.model_validate(data)

        # Verify
        # ===========================================================
        assert verified_user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_user_id(self) -> None:
        r"""Test the to initialize the model with an invalid `user_id`.

        `exceptions.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        data = {
            'success': True,
            'user_id': [],
            'sign_in_timestamp': '2024-04-27 18:23:52+02:00',
            'origin': 'https://ax7.com',
            'device': 'My device',
            'country': 'SE',
            'credential_nickname': 'credential_nickname',
            'credential_id': 'credential_id',
            'expires_at': '2024-04-27 19:23:52',
            'token_id': 'token_id',
            'type': 'type',
            'rp_id': 'rp_id',
        }

        data_exp = data.copy()
        data_exp['origin'] = AnyHttpUrl(data['origin'])  # type: ignore
        data_exp['sign_in_timestamp'] = datetime(2024, 4, 27, 18, 23, 52, tzinfo=ZoneInfo('CET'))
        data_exp['expires_at'] = datetime(2024, 4, 27, 19, 23, 52)

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            BitwardenPasswordlessVerifiedUser.model_validate(data)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'user_id' in error_msg, 'user_id not in error message!'

        # Clean up - None
        # ===========================================================

    def test_from_passwordless_verified_user(
        self,
        passwordless_verified_user: tuple[VerifiedUser, dict[str, Any]],
        bp_verified_user: tuple[BitwardenPasswordlessVerifiedUser, dict[str, Any]],
    ) -> None:
        r"""Test the alternative constructor method `_from_passwordless_verified_user`."""

        # Setup
        # ===========================================================
        input_verified_user, _ = passwordless_verified_user
        bp_verified_user_exp, _ = bp_verified_user

        # Exercise
        # ===========================================================
        bp_verified_user_result = (
            BitwardenPasswordlessVerifiedUser._from_passwordless_verified_user(input_verified_user)
        )

        # Verify
        # ===========================================================
        assert bp_verified_user_result.model_dump() == bp_verified_user_exp.model_dump()

        # Clean up - None
        # ===========================================================

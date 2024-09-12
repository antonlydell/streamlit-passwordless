r"""Unit tests for the backend module of the bitwarden_passwordless library."""

# Standard library
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import Mock
from zoneinfo import ZoneInfo

# Third party
import pytest
from passwordless import VerifiedUser
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless.backend import (
    BackendClient,
    BitwardenPasswordlessVerifiedUser,
    BitwardenRegisterConfig,
    PasswordlessError,
    _verify_sign_in_token,
)

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture()
def passwordless_verified_user() -> tuple[VerifiedUser, dict[str, Any]]:
    r"""An instance of `passwordless.VerifiedUser`.

    Returns
    -------
    verified_user : passwordless.VerifiedUser
        The verified user instance.

    data : dict[str, Any]
        The data used to create `verified_user`.
    """

    data = {
        'success': True,
        'user_id': 'user_id',
        'timestamp': datetime(2024, 4, 27, 18, 23, 52, tzinfo=ZoneInfo('CET')),
        'origin': 'https://ax7.com',
        'device': 'My device',
        'country': 'SE',
        'nickname': 'nickname',
        'credential_id': 'credential_id',
        'expires_at': datetime(2024, 4, 27, 19, 23, 52),
        'token_id': 'token_id',
        'type': 'type',
        'rp_id': 'rp_id',
    }
    verified_user = VerifiedUser(**data)

    return verified_user, data


@pytest.fixture()
def bp_verified_user(
    passwordless_verified_user: tuple[VerifiedUser, dict[str, Any]]
) -> tuple[BitwardenPasswordlessVerifiedUser, dict[str, Any]]:
    r"""An instance of `BitwardenPasswordlessVerifiedUser`.

    `BitwardenPasswordlessVerifiedUser` is the `streamlit_passwordless`
    implementation of `passwordless.VerifiedUser`.

    Returns
    -------
    bp_verified_user : bitwarden_passwordless.backend.BitwardenPasswordlessVerifiedUser
        The verified user instance.

    data : dict[str, Any]
        The data used to create `bp_verified_user`.
    """

    _, input_data = passwordless_verified_user

    data = input_data.copy()
    data['origin'] = AnyHttpUrl(input_data['origin'])  # type: ignore
    data['sign_in_timestamp'] = input_data['timestamp']
    del data['timestamp']
    data['credential_nickname'] = input_data['nickname']
    del data['nickname']

    bp_verified_user = BitwardenPasswordlessVerifiedUser.model_validate(data)

    return bp_verified_user, data


# =============================================================================================
# Tests
# =============================================================================================


class TestBitwardenRegisterConfig:
    r"""Tests for the `BitwardenRegisterConfig` model."""

    def test_expires_at_property_with_default_value_for_validity(
        self, mocked_get_current_datetime: datetime
    ) -> None:
        r"""Test the `expires_at` property with the default value for `validity`."""

        # Setup
        # ===========================================================
        validity = timedelta(seconds=120)
        expires_at_exp = mocked_get_current_datetime + validity

        # Exercise
        # ===========================================================
        config = BitwardenRegisterConfig()

        # Verify
        # ===========================================================
        assert config.expires_at == expires_at_exp

        # Clean up - None
        # ===========================================================

    def test_expires_at_property_with_custom_value_for_validity(
        self, mocked_get_current_datetime: datetime
    ) -> None:
        r"""Test the `expires_at` property with a custom value for `validity`."""

        # Setup
        # ===========================================================
        validity = timedelta(hours=1)
        expires_at_exp = mocked_get_current_datetime + validity

        # Exercise
        # ===========================================================
        config = BitwardenRegisterConfig(validity=validity)

        # Verify
        # ===========================================================
        assert config.expires_at == expires_at_exp

        # Clean up - None
        # ===========================================================


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


class TestVerifySignInToken:
    r"""Tests for the function `_verify_sign_in_token`."""

    def test_called_correctly(
        self,
        passwordless_verified_user: tuple[VerifiedUser, dict[str, Any]],
        bp_verified_user: tuple[BitwardenPasswordlessVerifiedUser, dict[str, Any]],
    ) -> None:
        r"""Test that the `_verify_sign_in_token` function can be called correctly."""

        # Setup
        # ===========================================================
        verified_user, _ = passwordless_verified_user
        bp_verified_user_exp, _ = bp_verified_user
        token = 'my_token'

        client = Mock(spec_set=BackendClient, name='MockedBackendClient')
        client.sign_in.return_value = verified_user

        # Exercise
        # ===========================================================
        bp_verified_user_result = _verify_sign_in_token(client=client, token=token)

        # Verify
        # ===========================================================
        assert bp_verified_user_result.model_dump() == bp_verified_user_exp.model_dump()

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_raises_sign_in_token_verification_error(self) -> None:
        r"""Test raising `SignInTokenVerificationError`.

        A raised `PasswordlessError` should be re-raised as a `SignInTokenVerificationError`.
        """

        # Setup
        # ===========================================================
        problem_details = {'error': True}
        token = 'my_token'

        client = Mock(spec_set=BackendClient, name='MockedBackendClient')
        client.sign_in.side_effect = PasswordlessError(problem_details=problem_details)

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.SignInTokenVerificationError) as exc_info:
            _verify_sign_in_token(client=client, token=token)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'Error verifying the sign in token!' in error_msg, 'Error message is incorrect!'
        assert f'{problem_details}' in error_msg, 'Error message problem_details are incorrect!'

        assert (
            problem_details == exc_info.value.data['problem_details']
        ), 'problem_details are incorrect!'

        assert token == exc_info.value.data['token'], 'token is incorrect!'

        # Clean up - None
        # ===========================================================

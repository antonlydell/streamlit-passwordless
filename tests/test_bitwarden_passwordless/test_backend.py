r"""Unit tests for the backend module of the bitwarden_passwordless library."""

# Standard library
from collections import namedtuple
from datetime import datetime, timedelta
from unittest.mock import Mock
from zoneinfo import ZoneInfo

# Third party
import pytest
from passwordless import VerifiedUser
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless import backend
from streamlit_passwordless.bitwarden_passwordless.backend import (
    BackendClient,
    BitwardenPasswordlessVerifiedUser,
    BitwardenRegisterConfig,
    PasswordlessError,
    RegisterToken,
    _build_backend_client,
    _create_register_token,
)

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


class TestBuildBackendClient:
    r"""Tests for the function `_build_backend_client`."""

    def test_build_backend_client(self) -> None:
        r"""Test building an instance of the backend client."""

        # Setup
        # ===========================================================
        private_key = 'private key'
        url = 'https://afterlife.ax7.com'

        # Exercise
        # ===========================================================
        client = _build_backend_client(private_key=private_key, url=url)

        # Verify
        # ===========================================================
        assert client.options.api_url == url, 'api_url is incorrect!'
        assert client.options.api_secret == private_key, 'api_secret is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_raises_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test that a raised exception will be re-raised as `StreamlitPasswordlessError`."""

        # Setup
        # ===========================================================
        error_msg_text = 'Unexpected!'
        error_msg_exp = f'Could not build Bitwarden backend client! ValueError : {error_msg_text}'
        monkeypatch.setattr(
            backend.PasswordlessClientBuilder,
            'build',
            Mock(side_effect=ValueError(error_msg_text)),
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            _build_backend_client(private_key='private_key', url='url')

        # Verify
        # ===========================================================
        exc_info_text = exc_info.exconly()
        print(exc_info_text)
        error_msg = exc_info.value.args[0]

        assert error_msg == error_msg_exp

        # Clean up - None
        # ===========================================================


class TestCreateRegisterToken:
    r"""Tests for the function `_create_register_token`."""

    def test_called_correctly(
        self, monkeypatch: pytest.MonkeyPatch, mocked_get_current_datetime: datetime
    ) -> None:
        r"""Test that the `_create_register_token` function can be called correctly."""

        # Setup
        # ===========================================================
        register_token_mock_return = namedtuple('register_token_mock_return', 'token')
        token_exp = 'syn.gates'

        user = models.User(username='SynGates')

        validity = timedelta(seconds=120)
        expires_at = mocked_get_current_datetime + validity
        monkeypatch.setattr(BitwardenRegisterConfig, 'expires_at', expires_at)

        client = Mock(spec_set=BackendClient, name='MockedBackendClient')
        client.register_token.return_value = register_token_mock_return(token=token_exp)

        bitwarden_register_config = BitwardenRegisterConfig()

        register_config = user.model_dump(
            exclude={'email', 'displayname'}
        ) | bitwarden_register_config.model_dump(exclude={'validity'})

        register_config['display_name'] = user.displayname
        register_config['expires_at'] = expires_at

        input_register_config_exp = RegisterToken(**register_config)

        # Exercise
        # ===========================================================
        token = _create_register_token(
            client=client, user=user, register_config=bitwarden_register_config
        )

        # Verify
        # ===========================================================
        assert token == token_exp, 'token is incorrect!'
        client.register_token.assert_called_once_with(register_token=input_register_config_exp)

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_raises_register_user_error(self) -> None:
        r"""Test that a raised `PasswordlessError` will be re-raised as a `RegisterUserError`."""

        # Setup
        # ===========================================================
        problem_details = {'error': True}
        user = models.User(username='SynGates')

        client = Mock(spec_set=BackendClient, name='MockedBackendClient')
        client.register_token.side_effect = PasswordlessError(problem_details=problem_details)

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.RegisterUserError) as exc_info:
            _create_register_token(
                client=client, user=user, register_config=BitwardenRegisterConfig()
            )

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'Error creating register token!' in error_msg, 'Error message is incorrect!'
        assert f'{problem_details}' in error_msg, 'Error message problem_details are incorrect!'

        assert (
            problem_details == exc_info.value.data['problem_details']
        ), 'problem_details are incorrect!'

        assert isinstance(
            exc_info.value.data['input_register_config'], RegisterToken
        ), 'input_register_config is incorrect!'

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

    def test_from_passwordless_verified_user(self) -> None:
        r"""Test the alternative constructor method `_from_passwordless_verified_user`."""

        # Setup
        # ===========================================================
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
        input_verified_user = VerifiedUser(**data)

        data_exp = data.copy()
        data_exp['origin'] = AnyHttpUrl(data['origin'])  # type: ignore
        data_exp['sign_in_timestamp'] = data['timestamp']
        del data_exp['timestamp']
        data_exp['credential_nickname'] = data['nickname']
        del data_exp['nickname']

        # Exercise
        # ===========================================================
        verified_user = BitwardenPasswordlessVerifiedUser._from_passwordless_verified_user(
            input_verified_user
        )

        # Verify
        # ===========================================================
        assert verified_user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

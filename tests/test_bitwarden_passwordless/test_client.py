r"""Unit tests for the client module of the bitwarden_passwordless library."""

# Standard library
from datetime import datetime, timedelta
from unittest.mock import Mock

# Third party
import pytest
from passwordless import PasswordlessError
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless.client import BitwardenPasswordlessClient

# =============================================================================================
# Tests
# =============================================================================================


class TestBitwardenPasswordlessClient:
    r"""Tests for the `BitwardenPasswordlessClient` model."""

    def test_init_with_defaults(self, mocked_get_current_datetime: datetime) -> None:
        r"""Test to initialize an instance with all default values."""

        # Setup
        # ===========================================================
        data = {
            'public_key': 'public key',
            'private_key': 'private key',
        }

        register_config_defaults = {
            'register_config': {
                'attestation': 'none',
                'authenticator_type': 'any',
                'discoverable': True,
                'user_verification': 'preferred',
                'validity': timedelta(seconds=120),
                'alias_hasing': True,
            },
        }

        data_exp = data | register_config_defaults
        data_exp['url'] = AnyHttpUrl('https://v4.passwordless.dev')  # type: ignore

        # Exercise
        # ===========================================================
        client = BitwardenPasswordlessClient.model_validate(data)

        # Verify
        # ===========================================================
        assert client.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_init_supply_all_parameters(self) -> None:
        r"""Test supply values for all parameters."""

        # Setup
        # ===========================================================
        data = {
            'url': 'http://ax7.com',
            'public_key': 'public key',
            'private_key': 'private key',
            'register_config': {
                'attestation': 'direct',
                'authenticator_type': 'cross-platform',
                'discoverable': False,
                'user_verification': 'required',
                'validity': timedelta(hours=1),
                'alias_hasing': False,
            },
        }

        data_exp = data.copy()
        data_exp['url'] = AnyHttpUrl(data['url'])  # type: ignore

        # Exercise
        # ===========================================================
        client = BitwardenPasswordlessClient.model_validate(data)

        # Verify
        # ===========================================================
        assert client.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_init_backend_client(self) -> None:
        r"""Test that the `_backend_client` attribute is instantiated correctly."""

        # Setup
        # ===========================================================
        url = 'https://ax7.com'
        url_exp = 'https://ax7.com/'
        private_key = 'private key'
        data = {
            'url': url,
            'public_key': 'public key',
            'private_key': private_key,
        }

        # Exercise
        # ===========================================================
        client = BitwardenPasswordlessClient.model_validate(data)

        # Verify
        # ===========================================================
        assert client._backend_client.options.api_url == url_exp, 'api_url is incorrect!'
        assert client._backend_client.options.api_secret == private_key, 'api_secret is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_url(self) -> None:
        r"""Test to supply an invalid url.

        A url without a http or https scheme is invalid.
        `exceptions.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup - None
        # ===========================================================
        data = {
            'url': 'ax7.com',
            'public_key': 'public key',
            'private_key': 'private key',
        }

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            BitwardenPasswordlessClient.model_validate(data)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'url' in error_msg, 'url not in error message!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_register_config(self) -> None:
        r"""Test to supply a register config that is partly invalid.

        "unsafe" is not a valid value for the key `authenticator_type`.
        `exceptions.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup - None
        # ===========================================================
        data = {
            'url': 'http://ax7.com',
            'public_key': 'public key',
            'private_key': 'private key',
            'register_config': {'attestation': 'indirect', 'authenticator_type': 'unsafe'},
        }

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            BitwardenPasswordlessClient.model_validate(data)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'authenticator_type' in error_msg, 'authenticator_type not in error message!'

        # Clean up - None
        # ===========================================================


class TestRegisterMethod:
    r"""Tests for the method `BitwardenPasswordlessClient.register_user`."""

    @pytest.mark.raises
    def test_backend_raises_register_user_error(
        self, user: models.User, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        r"""Test that `exceptions.RegisterUserError` can be properly raised.

        The Bitwarden Passwordless backend client should raise `passwordless.PasswordlessError`
        which should be re-raised as `exceptions.RegisterUserError` by the function
        `bitwarden_passwordless.backend._create_register_token`.
        """

        # Setup
        # ===========================================================
        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='public key', public_key='private key'
        )
        problem_details = {'error': True}

        monkeypatch.setattr(
            client._backend_client,
            'register_token',
            Mock(side_effect=PasswordlessError(problem_details=problem_details)),
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.RegisterUserError) as exc_info:
            client.register_user(user=user)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exc_info.value.data['problem_details'] == problem_details

        # Clean up - None
        # ===========================================================

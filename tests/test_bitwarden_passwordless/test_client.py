r"""Unit tests for the client module of the bitwarden_passwordless library."""

# Standard library
from datetime import datetime, timedelta
from unittest.mock import Mock

# Third party
import pytest
from pydantic import AnyHttpUrl

# Local
import streamlit_passwordless.bitwarden_passwordless.client
from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless.client import (
    BitwardenPasswordlessClient,
    backend,
)

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
                'alias_hashing': True,
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
                'alias_hashing': False,
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


class TestVerifySignInMethod:
    r"""Tests for the method `BitwardenPasswordlessClient.verify_sign_in`."""

    def test_called_correctly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test that the `verify_sign_in` method can be called correctly."""

        # Setup
        # ===========================================================
        token = 'token'

        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='private key', public_key='public_key'
        )

        m = Mock(
            spec_set=backend._verify_sign_in_token,
            name='mocked__verify_sign_in_function',
        )

        monkeypatch.setattr(
            streamlit_passwordless.bitwarden_passwordless.client.backend, '_verify_sign_in_token', m
        )

        # Exercise
        # ===========================================================
        client.verify_sign_in(token=token)

        # Verify
        # ===========================================================
        m.assert_called_once_with(client=client._backend_client, token=token)

        # Clean up - None
        # ===========================================================

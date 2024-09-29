r"""Unit tests for the backend module of the bitwarden_passwordless library."""

# Standard library
from datetime import datetime, timedelta
from unittest.mock import Mock, call
from zoneinfo import ZoneInfo

# Third party
import pytest
from passwordless import (
    Credential,
    CredentialDescriptor,
    PasswordlessClient,
    PasswordlessError,
    PasswordlessProblemDetails,
    RegisteredToken,
    RegisterToken,
    VerifiedUser,
)
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.bitwarden_passwordless import backend
from streamlit_passwordless.bitwarden_passwordless.backend import (
    BackendClient,
    BitwardenPasswordlessClient,
    BitwardenRegisterConfig,
)
from streamlit_passwordless.database import models as db_models

from ..config import ModelData

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture()
def list_of_credentials() -> tuple[list[Credential], str, list[Credential]]:
    r"""A list of passkey credentials with different origins.

    Returns
    -------
    credentials : list[Credential]

    origin_filter : str
        The origin to use for filtering `credentials`.

    credentials_filtered : list[Credential]
        The expected output after filtering credentials with `origin_filter`.
    """

    origin_filter = 'https://passkeys.example.com'
    tz = ZoneInfo('UTC')

    credentials = [
        Credential(
            descriptor=CredentialDescriptor(type='descriptor', id='1', transports=None),
            public_key='public_key_1',
            user_handle='user_handle_1',
            signature_counter=1,
            attestation_fmt='attestation',
            created_at=datetime(2024, 5, 14, 20, 34, 0, tzinfo=tz),
            aa_guid='aa_guid_1',
            last_user_at=datetime(2024, 6, 14, 21, 35, 2, tzinfo=tz),
            rp_id='passkeys.example.com',
            origin='https://passkeys.example.com',
            country='SE',
            device='iPhone 3GS',
            user_id='user_1',
        ),
        Credential(
            descriptor=CredentialDescriptor(type='descriptor', id='2', transports=None),
            public_key='public_key_2',
            user_handle='user_handle_1',
            signature_counter=10,
            attestation_fmt='attestation',
            created_at=datetime(2024, 3, 26, 10, 34, 0, tzinfo=tz),
            aa_guid='aa_guid_2',
            last_user_at=datetime(2024, 6, 15, 13, 23, 8, tzinfo=tz),
            rp_id='passkeys.example.com',
            origin='https://passkeys.example.com',
            country='SE',
            device='Windows XP',
            user_id='user_1',
        ),
        Credential(
            descriptor=CredentialDescriptor(type='descriptor', id='3', transports=None),
            public_key='public_key_3',
            user_handle='user_handle_2',
            signature_counter=15,
            attestation_fmt='attestation',
            created_at=datetime(2024, 1, 7, 18, 2, 23, tzinfo=tz),
            aa_guid='aa_guid_2',
            last_user_at=datetime(2024, 6, 6, 14, 12, 18, tzinfo=tz),
            rp_id='localhost:8501',
            origin='http://localhost:8501',
            country='DK',
            device='Windows 95',
            user_id='user_2',
        ),
    ]

    credentials_filtered = credentials[0:2].copy()

    return credentials, origin_filter, credentials_filtered


# =============================================================================================
# Tests
# =============================================================================================


class TestBitwardenRegisterConfig:
    r"""Tests for the `BitwardenRegisterConfig` model."""

    def test__init__(self) -> None:
        r"""Test to initialize an instance of `BitwardenRegisterConfig`."""

        # Setup
        # ===========================================================
        data = {
            'attestation': 'direct',
            'authenticator_type': 'platform',
            'discoverable': False,
            'user_verification': 'required',
            'validity': timedelta(seconds=240),
            'alias_hashing': False,
        }

        # Exercise
        # ===========================================================
        config = BitwardenRegisterConfig.model_validate(data)

        # Verify
        # ===========================================================
        assert config.model_dump() == data

        # Clean up - None
        # ===========================================================

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


class TestBitwardenPasswordlessClient:
    r"""Tests for the `BitwardenPasswordlessClient` model."""

    def test_init_with_defaults(self) -> None:
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
    def test_backend_client_raises_exception(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test raising a `PasswordlessError` from the backend client.

        The raised exception should re-raised as a `StreamlitPasswordlessError`.
        """

        # Setup
        # ===========================================================
        error_msg_exp = 'Could not build Bitwarden Passwordless backend client!'
        problem_details = PasswordlessProblemDetails(
            type='fake_error_type', title='error_title', status=400, error_code='error_code'
        )
        exception_to_raise = PasswordlessError(problem_details=problem_details)

        monkeypatch.setattr(
            backend.PasswordlessClientBuilder, 'build', Mock(side_effect=exception_to_raise)
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            BitwardenPasswordlessClient(public_key='public_key', private_key='private_key')

        # Verify
        # ===========================================================
        print(exc_info.exconly())
        e = exc_info.value  # The captured exception

        assert e.displayable_message == error_msg_exp, 'Error message is incorrect!'
        assert e.parent_exception is exception_to_raise, 'Parent exception is incorrect!'

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


class TestCreateRegisterTokenMethod:
    r"""Tests for the method `BitwardenPasswordlessClient.create_register_token`."""

    def test_called_correctly(
        self, user_1: tuple[models.User, db_models.User, ModelData], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        r"""Test that the `create_register_token` method can be called correctly."""

        # Setup
        # ===========================================================
        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='public key', public_key='private key'
        )
        register_token_exp = 'register_token'

        monkeypatch.setattr(
            client._backend_client,
            'register_token',
            Mock(
                return_value=RegisteredToken(register_token_exp),
                name='mocked_client._backend_client',
            ),
        )

        user, _, _ = user_1

        # Exercise
        # ===========================================================
        register_token = client.create_register_token(user=user)

        # Verify
        # ===========================================================
        print(f'{register_token=}')

        assert register_token == register_token_exp

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_backend_raises_register_user_error(
        self, user_1: tuple[models.User, db_models.User, ModelData], monkeypatch: pytest.MonkeyPatch
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

        problem_details = PasswordlessProblemDetails(
            type='fake_error_type', title='error_title', status=400, error_code='error_code'
        )
        exception_to_raise = PasswordlessError(problem_details=problem_details)

        monkeypatch.setattr(
            client._backend_client, 'register_token', Mock(side_effect=exception_to_raise)
        )

        user, _, _ = user_1

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.RegisterUserError) as exc_info:
            client.create_register_token(user=user)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)
        e = exc_info.value

        assert 'Error creating register token!' in error_msg, 'Error message is incorrect!'
        assert e.data['problem_details'] == problem_details, 'problem_details are incorrect!'
        assert isinstance(
            e.data['input_register_config'], RegisterToken
        ), 'input_register_config is incorrect!'

        # Clean up - None
        # ===========================================================


class TestVerifySignInMethod:
    r"""Tests for the method `BitwardenPasswordlessClient.verify_sign_in`."""

    def test_called_correctly(
        self,
        monkeypatch: pytest.MonkeyPatch,
        passwordless_verified_user: tuple[VerifiedUser, models.UserSignIn, ModelData],
    ) -> None:
        r"""Test that the `verify_sign_in` method can be called correctly."""

        # Setup
        # ===========================================================
        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='private key', public_key='public_key'
        )
        verified_user, user_sign_in_exp, _ = passwordless_verified_user

        m = Mock(
            spec_set=client._backend_client.sign_in,
            name='mocked__backend_client_sign_in',
            return_value=verified_user,
        )
        monkeypatch.setattr(client._backend_client, 'sign_in', m)

        # Exercise
        # ===========================================================
        user_sign_in_result = client.verify_sign_in(token='token')

        # Verify
        # ===========================================================
        assert user_sign_in_result.model_dump() == user_sign_in_exp.model_dump()

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_raises_sign_in_token_verification_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test raising `SignInTokenVerificationError`.

        A raised `PasswordlessError` should be re-raised as a `SignInTokenVerificationError`.
        """

        # Setup
        # ===========================================================
        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='public key', public_key='private key'
        )
        token = 'my_token'

        problem_details = PasswordlessProblemDetails(
            type='fake_error_type', title='error_title', status=400, error_code='error_code'
        )
        exception_to_raise = PasswordlessError(problem_details=problem_details)

        m = Mock(
            spec_set=BackendClient.sign_in,
            name='mocked__backend_client_sign_in',
            side_effect=exception_to_raise,
        )
        monkeypatch.setattr(client._backend_client, 'sign_in', m)

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.SignInTokenVerificationError) as exc_info:
            client.verify_sign_in(token=token)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)
        e = exc_info.value

        assert 'Error verifying the sign in token!' in error_msg, 'Error message is incorrect!'
        assert str(problem_details) in error_msg, 'Error message problem_details are incorrect!'
        assert problem_details == e.data['problem_details'], 'problem_details are incorrect!'
        assert token == e.data['token'], 'token is incorrect!'

        # Clean up - None
        # ===========================================================


class TestGetCredentialsMethod:
    r"""Tests for the method `BitwardenPasswordlessClient.get_credentials`."""

    def test_called_correctly(
        self,
        list_of_credentials: tuple[list[Credential], str, list[Credential]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test that the `get_credentials` method can be called correctly."""

        # Setup
        # ===========================================================
        credentials, _, _ = list_of_credentials
        user_id = 'user_1'

        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='private_key', public_key='public_key'
        )

        m = Mock(
            spec_set=PasswordlessClient.get_credentials,
            name='mocked__backend_client.get_credentials',
            return_value=credentials,
        )

        monkeypatch.setattr(client._backend_client, 'get_credentials', m)

        # Exercise
        # ===========================================================
        credentials_result = client.get_credentials(user_id=user_id)

        # Verify
        # ===========================================================
        m.assert_called_once()
        assert m.call_args == call(user_id=user_id), 'call_args are incorrect!'
        assert credentials_result == credentials, 'credentials are incorrect!'

        # Clean up - None
        # ===========================================================

    def test_filter_by_origin(
        self,
        list_of_credentials: tuple[list[Credential], str, list[Credential]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test to filter the credentials by their origin."""

        # Setup
        # ===========================================================
        credentials, origin_filter, exp_credentials = list_of_credentials
        user_id = 'user_1'

        client = BitwardenPasswordlessClient(
            url='https://ax7.com', private_key='private_key', public_key='public_key'
        )

        m = Mock(
            spec_set=PasswordlessClient.get_credentials,
            name='mocked__backend_client.get_credentials',
            return_value=credentials,
        )

        monkeypatch.setattr(client._backend_client, 'get_credentials', m)

        # Exercise
        # ===========================================================
        credentials_result = client.get_credentials(user_id=user_id, origin=origin_filter)

        # Verify
        # ===========================================================
        m.assert_called_once()
        assert m.call_args == call(user_id=user_id), 'call_args are incorrect!'
        assert credentials_result == exp_credentials, 'credentials are incorrect!'

        # Clean up - None
        # ===========================================================

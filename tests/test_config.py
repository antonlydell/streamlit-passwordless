r"""Unit tests for the config module of Streamlit Passwordless."""

# Standard library
from typing import ClassVar

# Third party
import pytest
from pydantic import AnyHttpUrl, ValidationError
from sqlalchemy import URL, make_url

# Local
from streamlit_passwordless import config, exceptions
from streamlit_passwordless.bitwarden_passwordless import BITWARDEN_PASSWORDLESS_API_URL
from streamlit_passwordless.config import (
    STP_BWP_PRIVATE_KEY,
    STP_BWP_PUBLIC_KEY,
    STP_BWP_URL,
    STP_DB_URL,
    STP_SECRETS_SECTION,
    ConfigManager,
)

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture()
def mocked_streamlit_secrets(monkeypatch: pytest.MonkeyPatch) -> ConfigManager:
    r"""Mock `streamlit.secrets` with configuration for Streamlit Passwordless.

    Returns
    -------
    cm : streamlit_passwordless.ConfigManager
        A config manager with the expected configuration loaded from
        the mocked `streamlit.secrets`.
    """

    secrets = {
        STP_SECRETS_SECTION: {
            STP_BWP_PUBLIC_KEY: 'public_key',
            STP_BWP_PRIVATE_KEY: 'private_key',
            STP_BWP_URL: 'https://bwp_url.com',
            STP_DB_URL: 'sqlite:///mocked.db',
        },
        'some_other_section': {'test': 123},
    }
    exp_config = {
        'bwp_public_key': 'public_key',
        'bwp_private_key': 'private_key',
        'bwp_url': AnyHttpUrl('https://bwp_url.com'),  # type: ignore
        'db_url': make_url('sqlite:///mocked.db'),
    }
    monkeypatch.setattr(config.st, 'secrets', secrets)

    cm = ConfigManager.model_validate(exp_config)

    return cm


# =============================================================================================
# Tests
# =============================================================================================


class TestConfigManagerInit:
    r"""Tests for initializing `streamlit_passwordless.ConfigManager`.

    The ConfigManager handles the configuration for a Streamlit Passwordless application.
    """

    bwp_public_key: ClassVar[str] = 'bwp_public_key'
    bwp_private_key: ClassVar[str] = 'bwp_private_key'

    def test_init_with_default_values(self) -> None:
        r"""Test to initialize `ConfigManager` with the minimum config needed.

        The config values not specified should be filled in with the default values.
        """

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager(bwp_public_key=self.bwp_public_key, bwp_private_key=self.bwp_private_key)

        # Verify
        # ===========================================================
        assert cm.bwp_public_key == self.bwp_public_key, 'bwp_public_key is incorrect!'
        assert cm.bwp_private_key == self.bwp_private_key, 'bwp_private_key is incorrect!'
        assert cm.bwp_url == BITWARDEN_PASSWORDLESS_API_URL, 'bwp_url is incorrect!'
        assert cm.db_url == make_url('sqlite:///streamlit_passwordless.db'), 'db_url is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'bwp_url, exp_bwp_url',
        (
            pytest.param(
                'http://test.com', AnyHttpUrl('http://test.com'), id='str'  # type: ignore
            ),
            pytest.param(
                AnyHttpUrl('https://test.com'), AnyHttpUrl('https://test.com'), id='AnyHttpUrl'  # type: ignore
            ),
        ),
    )
    def test_bwp_url(self, bwp_url: str | AnyHttpUrl, exp_bwp_url: AnyHttpUrl) -> None:
        r"""Test the `bwp_url` parameter of `ConfigManager`."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager(
            bwp_public_key=self.bwp_public_key,
            bwp_private_key=self.bwp_private_key,
            bwp_url=bwp_url,  # type: ignore
        )

        # Verify
        # ===========================================================
        assert cm.bwp_url == exp_bwp_url, 'bwp_url is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'db_url, exp_db_url',
        (
            pytest.param(
                'sqlite:///test.db', make_url('sqlite:///test.db'), id='str'  # type: ignore
            ),
            pytest.param(make_url('sqlite://'), make_url('sqlite://'), id='URL'),  # type: ignore
        ),
    )
    def test_db_url(self, db_url: str | URL, exp_db_url: URL) -> None:
        r"""Test the `db_url` parameter of `ConfigManager`."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager(
            bwp_public_key=self.bwp_public_key, bwp_private_key=self.bwp_private_key, db_url=db_url
        )

        # Verify
        # ===========================================================
        assert cm.db_url == exp_db_url, 'db_url is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_bwp_url(self) -> None:
        r"""Test to provide an invalid http url for Bitwarden Passwordless.

        `streamlit_passwordless.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        bwp_url = 'htt://invalid.com'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            ConfigManager(
                bwp_public_key=self.bwp_public_key,
                bwp_private_key=self.bwp_private_key,
                bwp_url=bwp_url,  # type: ignore
            )

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert bwp_url in error_msg, 'bwp_url not in error_msg!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_db_url(self) -> None:
        r"""Test to provide an invalid database url.

        `streamlit_passwordless.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        db_url = 'sqlite::///invalid.db'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            ConfigManager(
                bwp_public_key=self.bwp_public_key,
                bwp_private_key=self.bwp_private_key,
                db_url=db_url,
            )

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'DatabaseInvalidUrlError' in error_msg, 'DatabaseInvalidUrlError not in error_msg!'
        assert db_url in error_msg, 'db_url not in error_msg!'

        # Clean up - None
        # ===========================================================

    def test_from_aliases(self) -> None:
        r"""Test to initialize `ConfigManager` using parameter aliases."""

        # Setup
        # ===========================================================
        data = {
            STP_BWP_PUBLIC_KEY: 'public_key',
            STP_BWP_PRIVATE_KEY: 'private_key',
            STP_BWP_URL: 'https://bwp_url.com',
            STP_DB_URL: 'sqlite:///mocked.db',
        }
        exp_cm = ConfigManager(
            bwp_public_key='public_key',
            bwp_private_key='private_key',
            bwp_url='https://bwp_url.com',  # type: ignore
            db_url='sqlite:///mocked.db',
        )

        # Exercise
        # ===========================================================
        cm = ConfigManager.model_validate(data)

        # Verify
        # ===========================================================
        assert cm == exp_cm

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_is_immutable(self) -> None:
        r"""Test that `ConfigManager` is immutable.

        `pydantic.ValidationError` is expected to be raised when an attribute
        of `ConfigManager` is trying to be changed after the instance is created.
        """

        # Setup
        # ===========================================================
        cm = ConfigManager(bwp_public_key=self.bwp_public_key, bwp_private_key=self.bwp_private_key)

        # Exercise
        # ===========================================================
        with pytest.raises(ValidationError) as exc_info:
            cm.bwp_public_key = ''  # type: ignore

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'bwp_public_key' in error_msg, 'bwp_public_key not in error_msg!'

        # Clean up - None
        # ===========================================================


class TestConfigManagerLoad:
    r"""Tests for the classmethod `ConfigManager.load`."""

    def test_from_streamlit_secrets(self, mocked_streamlit_secrets: ConfigManager) -> None:
        r"""Test to load the config from `streamlit.secrets`.

        All config keys are defined and no environment variables are specified.
        """

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager.load()

        # Verify
        # ===========================================================
        assert cm == mocked_streamlit_secrets

        # Clean up - None
        # ===========================================================

    def test_from_streamlit_secrets_override_with_env_variables(
        self, mocked_streamlit_secrets: ConfigManager, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        r"""Test to load the config from `streamlit.secrets`.

        The config key `bwp_private_key` is overridden by a value from
        an environment variable.
        """

        # Setup
        # ===========================================================
        private_key_env_var = 'private_key_env_var'
        monkeypatch.setenv(STP_BWP_PRIVATE_KEY, private_key_env_var)
        cm_exp = ConfigManager(
            bwp_public_key=mocked_streamlit_secrets.bwp_public_key,
            bwp_private_key=private_key_env_var,
            bwp_url=mocked_streamlit_secrets.bwp_url,
            db_url=mocked_streamlit_secrets.db_url,
        )

        # Exercise
        # ===========================================================
        cm = ConfigManager.load()

        # Verify
        # ===========================================================
        assert cm == cm_exp

        # Clean up - None
        # ===========================================================

    def test_from_empty_streamlit_secrets_override_with_env_variables(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        r"""Test to load the config from an empty `streamlit.secrets`.

        The config keys `bwp_public_key` and `bwp_private_key` are
        fetched from environment variables.
        """

        # Setup
        # ===========================================================
        public_key_env_var = 'public_key_env_var'
        monkeypatch.setenv(STP_BWP_PUBLIC_KEY, public_key_env_var)

        private_key_env_var = 'private_key_env_var'
        monkeypatch.setenv(STP_BWP_PRIVATE_KEY, private_key_env_var)

        monkeypatch.setattr(config.st, 'secrets', {})

        cm_exp = ConfigManager(
            bwp_public_key=public_key_env_var, bwp_private_key=private_key_env_var
        )

        # Exercise
        # ===========================================================
        cm = ConfigManager.load()

        # Verify
        # ===========================================================
        assert cm == cm_exp

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_no_config_defined(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test to load the config when no configuration is defined.

        `streamlit_passwordless.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        monkeypatch.setattr(config.st, 'secrets', {})
        for env_var in (STP_BWP_PUBLIC_KEY, STP_BWP_PRIVATE_KEY, STP_BWP_URL, STP_DB_URL):
            monkeypatch.delenv(env_var, raising=False)

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            ConfigManager.load()

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'bwp_public_key' in error_msg, 'bwp_public_key not in error_msg!'
        assert 'bwp_private_key' in error_msg, 'bwp_private_key not in error_msg!'

        # Clean up - None
        # ===========================================================

r"""Unit tests for the backend module of the bitwarden_passwordless library."""

# Standard library
from datetime import datetime, timedelta

# Local
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenRegisterConfig

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

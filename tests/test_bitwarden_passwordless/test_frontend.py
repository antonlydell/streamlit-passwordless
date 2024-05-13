r"""Unit tests for the frontend module of the bitwarden_passwordless library."""

# Standard library
from unittest.mock import Mock

# Third party
import pytest

# Local
import streamlit_passwordless.bitwarden_passwordless.frontend
from streamlit_passwordless.bitwarden_passwordless.frontend import (
    _bitwarden_passwordless_func,
    register_button,
    sign_in_button,
)

# =============================================================================================
# Tests
# =============================================================================================


class TestRegisterButton:
    r"""Tests for the function `register_button`."""

    def test_called_correctly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test that the `register_button` function can be called correctly."""

        # Setup
        # ===========================================================
        register_token = 'register_token'
        public_key = 'public_key'
        credential_nickname = 'credential_nickname'
        disabled = True
        key = 'key'
        return_value = ('token', None, 1)

        m = Mock(
            spec_set=_bitwarden_passwordless_func,
            return_value=return_value,
            name='mocked_javascript_func',
        )

        monkeypatch.setattr(
            streamlit_passwordless.bitwarden_passwordless.frontend,
            '_bitwarden_passwordless_func',
            m,
        )

        # Exercise
        # ===========================================================
        token, error, clicked = register_button(
            register_token=register_token,
            public_key=public_key,
            credential_nickname=credential_nickname,
            disabled=disabled,
            key=key,
        )

        # Verify
        # ===========================================================
        m.assert_called_once_with(
            action='register',
            register_token=register_token,
            public_key=public_key,
            credential_nickname=credential_nickname,
            disabled=disabled,
            key=key,
        )
        assert token == return_value[0], 'token is incorrect!'
        assert error == return_value[1], 'error is incorrect!'
        assert clicked is True, 'clicked is incorrect!'

        # Clean up - None
        # ===========================================================


class TestSignInButton:
    r"""Tests for the function `sign_in_button`."""

    def test_called_correctly(self, monkeypatch: pytest.MonkeyPatch) -> None:
        r"""Test that the `sign_in_button` function can be called correctly."""

        # Setup
        # ===========================================================
        public_key = 'public_key'
        alias = 'syn.gates'
        with_discoverable = True
        with_autofill = False
        disabled = False
        key = 'key'

        return_value = ('token', None, 1)

        m = Mock(
            spec_set=_bitwarden_passwordless_func,
            return_value=return_value,
            name='mocked_javascript_func',
        )

        monkeypatch.setattr(
            streamlit_passwordless.bitwarden_passwordless.frontend,
            '_bitwarden_passwordless_func',
            m,
        )

        # Exercise
        # ===========================================================
        token, error, clicked = sign_in_button(
            public_key=public_key,
            alias=alias,
            with_discoverable=with_discoverable,
            with_autofill=with_autofill,
            disabled=disabled,
            key=key,
        )

        # Verify
        # ===========================================================
        m.assert_called_once_with(
            action='sign_in',
            public_key=public_key,
            alias=alias,
            with_discoverable=with_discoverable,
            with_autofill=with_autofill,
            disabled=disabled,
            key=key,
        )
        assert token == return_value[0], 'token is incorrect!'
        assert error == return_value[1], 'error is incorrect!'
        assert clicked is True, 'clicked is incorrect!'

        # Clean up - None
        # ===========================================================

r"""Unit tests for the frontend module of the bitwarden_passwordless library."""

# Standard library
from typing import Any
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
# Fixtures
# =============================================================================================


@pytest.fixture()
def mocked_session_state(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    r"""Mock the session state with an empty dictionary.

    Returns
    -------
    session_state : dict[str, Any]
        The mocked session state.
    """

    session_state: dict[str, Any] = {}
    monkeypatch.setattr(
        streamlit_passwordless.bitwarden_passwordless.frontend.st, 'session_state', session_state
    )

    return session_state


# =============================================================================================
# Tests
# =============================================================================================


class TestRegisterButton:
    r"""Tests for the function `register_button`."""

    @pytest.mark.parametrize(
        'session_state_nr_clicks, is_clicked_exp',
        (pytest.param(0, True, id='clicked'), pytest.param(1, False, id='not clicked')),
    )
    def test_clicked(
        self,
        session_state_nr_clicks: int,
        is_clicked_exp: bool,
        mocked_session_state: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test clicking the `register_button`.

        If the returned click count from `register_button` is greater than the previous
        click count in the session state the button should be identified as clicked.

        Parameters
        ----------
        session_state_nr_clicks : int
            The mocked session state click count of the `register_button`.

        is_clicked_exp : bool
            The expected result if the `register_button` has been clicked or not.
        """

        # Setup
        # ===========================================================
        register_token = 'register_token'
        public_key = 'public_key'
        credential_nickname = 'credential_nickname'
        disabled = True
        label = 'Register Button'
        key = 'key'
        session_state_key = f'_{key}-nr-clicks'
        mocked_session_state[session_state_key] = session_state_nr_clicks

        return_value = ('token', None, 1)  # (token, error, nr_clicks)

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
            label=label,
            button_type='secondary',
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
            label=label,
            button_type='secondary',
            key=key,
        )
        assert token == return_value[0], 'token is incorrect!'
        assert error is return_value[1], 'error is incorrect!'
        assert clicked is is_clicked_exp, 'clicked is incorrect!'

        # Clean up - None
        # ===========================================================


class TestSignInButton:
    r"""Tests for the function `sign_in_button`."""

    @pytest.mark.parametrize(
        'session_state_nr_clicks, is_clicked_exp',
        (pytest.param(0, True, id='clicked'), pytest.param(1, False, id='not clicked')),
    )
    def test_clicked(
        self,
        session_state_nr_clicks: int,
        is_clicked_exp: bool,
        mocked_session_state: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test clicking the `sign_in_button`.

        If the returned click count from `sign_in_button` is greater than the previous
        click count in the session state the button should be identified as clicked.

        Parameters
        ----------
        session_state_nr_clicks : int
            The mocked session state click count of the `sign_in_button`.

        is_clicked_exp : bool
            The expected result if the `sign_in_button` has been clicked or not.
        """

        # Setup
        # ===========================================================
        public_key = 'public_key'
        alias = 'syn.gates'
        with_discoverable = True
        with_autofill = False
        disabled = False
        label = 'Sign in Button'
        key = 'key'
        session_state_key = f'_{key}-nr-clicks'
        mocked_session_state[session_state_key] = session_state_nr_clicks

        return_value = ('token', None, 1)  # (token, error, nr_clicks)

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
            label=label,
            button_type='primary',
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
            label=label,
            button_type='primary',
            key=key,
        )
        assert token == return_value[0], 'token is incorrect!'
        assert error is return_value[1], 'error is incorrect!'
        assert clicked is is_clicked_exp, 'clicked is incorrect!'

        # Clean up - None
        # ===========================================================

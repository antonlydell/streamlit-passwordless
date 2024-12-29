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


@pytest.fixture()
def mocked__bitwarden_passwordless_func_return_tuple(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Mock, tuple[str, None]]:
    r"""Mock the function `_bitwarden_passwordless_func` to return a tuple.

    Returns
    -------
    m : Mock
        The mock for `_bitwarden_passwordless_func`.

    return_value : tuple[str, None]
        The return value from `_bitwarden_passwordless_func`.
    """

    return_value = ('token', None)  # (token, error)

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

    return m, return_value


@pytest.fixture()
def mocked__bitwarden_passwordless_func_return_tuple_with_error(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Mock, tuple[str, str]]:
    r"""Mock the function `_bitwarden_passwordless_func` to return a tuple.

    The error value being returned is not None.

    Returns
    -------
    m : Mock
        The mock for `_bitwarden_passwordless_func`.

    return_value : tuple[str, str]
        The return value from `_bitwarden_passwordless_func`.
    """

    return_value = ('token', 'Error!')  # (token, error)

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

    return m, return_value


@pytest.fixture()
def mocked__bitwarden_passwordless_func_return_none(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Mock, tuple[str, None]]:
    r"""Mock the function `_bitwarden_passwordless_func` to return None.

    Returns
    -------
    m : Mock
        The mock for `_bitwarden_passwordless_func`.

    return_value : tuple[str, None]
        The expected return value from `sign_in_button` or `register_button`.
    """

    return_value = ('', None)  # (token, error)

    m = Mock(
        spec_set=_bitwarden_passwordless_func,
        return_value=None,
        name='mocked_javascript_func',
    )

    monkeypatch.setattr(
        streamlit_passwordless.bitwarden_passwordless.frontend,
        '_bitwarden_passwordless_func',
        m,
    )

    return m, return_value


# =============================================================================================
# Tests
# =============================================================================================


class TestRegisterButton:
    r"""Tests for the function `register_button`."""

    @pytest.mark.parametrize(
        'session_state_previous_token, is_clicked_exp',
        (
            pytest.param('not token', True, id='clicked'),
            pytest.param('token', False, id='not clicked'),
        ),
    )
    def test_clicked(
        self,
        session_state_previous_token: str,
        is_clicked_exp: bool,
        mocked_session_state: dict[str, Any],
        mocked__bitwarden_passwordless_func_return_tuple: tuple[Mock, tuple[str, None]],
    ) -> None:
        r"""Test clicking the `register_button`.

        If the returned token from `register_button` is the same as the previous token
        in the session state the button should be identified as clicked.

        Parameters
        ----------
        session_state_previous_token : str
            The mocked session state for the previous register token of the `register_button`.

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
        session_state_key = f'_{key}-previous-token'
        mocked_session_state[session_state_key] = session_state_previous_token

        m, return_value = mocked__bitwarden_passwordless_func_return_tuple

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

    @pytest.mark.parametrize(
        'session_state_previous_token, is_clicked_exp',
        (
            pytest.param('not token', True, id='token not equals previous'),
            pytest.param('token', True, id='token equals previous'),
        ),
    )
    def test_clicked_when_error_is_returned(
        self,
        session_state_previous_token: str,
        is_clicked_exp: bool,
        mocked_session_state: dict[str, Any],
        mocked__bitwarden_passwordless_func_return_tuple_with_error: tuple[Mock, tuple[str, str]],
    ) -> None:
        r"""Test clicking the `register_button`.

        The error value returned from `_bitwarden_passwordless_func` is not None and
        the button should be identified as clicked.

        Parameters
        ----------
        session_state_previous_token : str
            The mocked session state for the previous register token of the `register_button`.

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
        session_state_key = f'_{key}-previous-token'
        mocked_session_state[session_state_key] = session_state_previous_token

        m, return_value = mocked__bitwarden_passwordless_func_return_tuple_with_error

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

    def test_return_none(
        self,
        mocked_session_state: dict[str, Any],
        mocked__bitwarden_passwordless_func_return_none: tuple[Mock, tuple[str, None]],
    ) -> None:
        r"""Test the return value when `_bitwarden_passwordless_func` returns None.

        ('', None, False) is expected to be returned from `register_button`.
        """

        # Setup
        # ===========================================================
        register_token = 'register_token'
        public_key = 'public_key'
        credential_nickname = 'credential_nickname'
        disabled = True
        label = 'Register Button'
        key = 'key'

        m, return_value = mocked__bitwarden_passwordless_func_return_none
        exp_result = (return_value[0], return_value[1], False)

        # Exercise
        # ===========================================================
        result = register_button(
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
        assert result == exp_result, 'result is incorrect!'
        assert mocked_session_state == {}, 'The session state has been modified!'

        # Clean up - None
        # ===========================================================


class TestSignInButton:
    r"""Tests for the function `sign_in_button`."""

    @pytest.mark.parametrize(
        'session_state_previous_token, is_clicked_exp',
        (
            pytest.param('not token', True, id='clicked'),
            pytest.param('token', False, id='not clicked'),
        ),
    )
    def test_clicked(
        self,
        session_state_previous_token: str,
        is_clicked_exp: bool,
        mocked_session_state: dict[str, Any],
        mocked__bitwarden_passwordless_func_return_tuple: tuple[Mock, tuple[str, None, int]],
    ) -> None:
        r"""Test clicking the `sign_in_button`.

        If the returned token from `sign_in_button` is the same as the previous token
        in the session state the button should be identified as clicked.

        Parameters
        ----------
        session_state_previous_token : str
            The mocked session state for the previous sign-in token of the `sign_in_button`.

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
        session_state_key = f'_{key}-previous-token'
        mocked_session_state[session_state_key] = session_state_previous_token

        m, return_value = mocked__bitwarden_passwordless_func_return_tuple

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

    @pytest.mark.parametrize(
        'session_state_previous_token, is_clicked_exp',
        (
            pytest.param('not token', True, id='token not equals previous'),
            pytest.param('token', True, id='token equals previous'),
        ),
    )
    def test_clicked_when_error_is_returned(
        self,
        session_state_previous_token: str,
        is_clicked_exp: bool,
        mocked_session_state: dict[str, Any],
        mocked__bitwarden_passwordless_func_return_tuple_with_error: tuple[Mock, tuple[str, str]],
    ) -> None:
        r"""Test clicking the `sign_in_button`.

        The error value returned from `_bitwarden_passwordless_func` is not None and
        the button should be identified as clicked.

        Parameters
        ----------
        session_state_previous_token : str
            The mocked session state for the previous sign-in token of the `sign_in_button`.

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
        session_state_key = f'_{key}-previous-token'
        mocked_session_state[session_state_key] = session_state_previous_token

        m, return_value = mocked__bitwarden_passwordless_func_return_tuple_with_error

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

    def test_return_none(
        self,
        mocked_session_state: dict[str, Any],
        mocked__bitwarden_passwordless_func_return_none: tuple[Mock, tuple[str, None]],
    ) -> None:
        r"""Test the return value when `_bitwarden_passwordless_func` returns None.

        ('', None, False) is expected to be returned from `sign_in_button`.
        """

        # Setup
        # ===========================================================
        register_token = 'register_token'
        public_key = 'public_key'
        credential_nickname = 'credential_nickname'
        disabled = True
        label = 'Sign In Button'
        key = 'key'

        m, return_value = mocked__bitwarden_passwordless_func_return_none
        exp_result = (return_value[0], return_value[1], False)

        # Exercise
        # ===========================================================
        result = register_button(
            register_token=register_token,
            public_key=public_key,
            credential_nickname=credential_nickname,
            disabled=disabled,
            label=label,
            button_type='primary',
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
            button_type='primary',
            key=key,
        )
        assert result == exp_result, 'result is incorrect!'
        assert mocked_session_state == {}, 'The session state has been modified!'

        # Clean up - None
        # ===========================================================

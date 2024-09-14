r"""Fixtures for testing streamlit-passwordless."""

# Standard library
from datetime import datetime
from typing import Any
from unittest.mock import Mock
from zoneinfo import ZoneInfo

# Third party
import pytest
from passwordless import VerifiedUser
from pydantic import AnyHttpUrl

# Local
import streamlit_passwordless.bitwarden_passwordless.backend
from streamlit_passwordless import common, models
from streamlit_passwordless.bitwarden_passwordless.backend import BitwardenPasswordlessVerifiedUser

# =============================================================================================
# Models
# =============================================================================================


@pytest.fixture(scope='session')
def user_id() -> str:
    r"""The user ID to use for the test user of the test suite."""

    return 'mocked-user_id'


@pytest.fixture()
def mocked_user_id(user_id: str, monkeypatch: pytest.MonkeyPatch) -> str:
    r"""Mock the user ID that is generated if a user ID is not supplied to the `User` model.

    Returns
    -------
    user_id : str
        The user_id that is returned from the mock.
    """

    monkeypatch.setattr(models.uuid, 'uuid4', Mock(return_value=user_id))

    return user_id


@pytest.fixture(scope='session')
def user(user_id: str) -> models.User:
    r"""A test user to use for the test suite.

    Returns
    -------
    streamlit_passwordless.models.User
    """

    return models.User(
        username='m.shadows',
        user_id=user_id,
        email='m.shadows@ax7.com',
        displayname='M Shadows',
        aliases=('Matt', 'Shadows'),
    )


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
# Common
# =============================================================================================


@pytest.fixture()
def mocked_get_current_datetime(monkeypatch: pytest.MonkeyPatch) -> datetime:
    r"""Set the current datetime to a fixed value.

    Returns
    -------
    now : datetime
        The current datetime fixed to 2023-10-20 13:37:37.
    """

    now = datetime(2023, 10, 20, 13, 37, 37, tzinfo=ZoneInfo('UTC'))
    m = Mock(spec_set=common.get_current_datetime, return_value=now)

    monkeypatch.setattr(
        streamlit_passwordless.bitwarden_passwordless.backend.common, 'get_current_datetime', m
    )

    return now

r"""Fixtures for testing streamlit-passwordless."""

# Standard library
from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

# Third party
import pytest

# Local
import streamlit_passwordless.bitwarden_passwordless.backend
from streamlit_passwordless import common, models

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

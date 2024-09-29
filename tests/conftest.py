r"""Fixtures for testing streamlit-passwordless."""

# Standard library
from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

# Third party
import pytest
from passwordless import VerifiedUser

# Local
import streamlit_passwordless.bitwarden_passwordless.backend
from streamlit_passwordless import common, models
from streamlit_passwordless.database import models as db_models

from .config import TZ_UTC, ModelData

# =============================================================================================
# Models
# =============================================================================================


@pytest.fixture(scope='session')
def user_1_user_id() -> str:
    r"""The user ID for test user 1 of the test suite."""

    return 'user_1_user_id'


@pytest.fixture()
def mocked_user_id(user_1_user_id: str, monkeypatch: pytest.MonkeyPatch) -> str:
    r"""Mock the user ID that is generated if a user ID is not supplied to the `User` model.

    Returns
    -------
    user_id : str
        The user_id that is returned from the mock.
    """

    monkeypatch.setattr(models.uuid, 'uuid4', Mock(return_value=user_1_user_id))

    return user_1_user_id


@pytest.fixture(scope='session')
def user_1_email_primary(user_1_user_id: str) -> tuple[models.Email, db_models.Email, ModelData]:
    r"""The primary email of test user 1.

    Returns
    -------
    model : streamlit_passwordless.models.Email
        The model of the email address.

    db_model : streamlit_passwordless.database.models.Email
        The database model of the email address.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'email_id': 1,
        'user_id': user_1_user_id,
        'email': 'rev@ax7.com',
        'is_primary': True,
        'verified_at': datetime(1999, 1, 1, 1, 1, 1, tzinfo=TZ_UTC),
        'disabled': False,
        'disabled_timestamp': None,
    }

    model = models.Email.model_validate(data)
    db_model = db_models.Email(**data)

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1_email_secondary(user_1_user_id: str) -> tuple[models.Email, db_models.Email, ModelData]:
    r"""The secondary email of test user 1.

    Returns
    -------
    model : streamlit_passwordless.models.Email
        The model of the email address.

    db_model : streamlit_passwordless.database.models.Email
        The database model of the email address.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'email_id': 2,
        'user_id': user_1_user_id,
        'email': 'the.rev@ax7.com',
        'is_primary': False,
        'verified_at': None,
        'disabled': True,
        'disabled_timestamp': datetime(2007, 10, 30, 12, 0, 0, tzinfo=TZ_UTC),
    }

    model = models.Email.model_validate(data)
    db_model = db_models.Email(**data)

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1_sign_in_successful(
    user_1_user_id: str,
) -> tuple[models.UserSignIn, db_models.UserSignIn, ModelData]:
    r"""A successful passkey sign in for test user 1.

    Returns
    -------
    model : streamlit_passwordless.models.UserSignIn
        The model of the user sign in.

    db_model : streamlit_passwordless.database.models.UserSignIn
        The database model of the user sign in.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'user_sign_in_id': 1,
        'user_id': user_1_user_id,
        'sign_in_timestamp': datetime(2005, 6, 6, 13, 37, 37, tzinfo=TZ_UTC),
        'success': True,
        'origin': 'http://localhost:8501/',
        'device': 'Google Chrome',
        'country': 'US',
        'credential_nickname': 'beast_and_the_harlot',
        'credential_id': 'credential_id_1',
        'sign_in_type': 'passkey_signin',
        'rp_id': None,
    }

    model = models.UserSignIn.model_validate(data)
    db_model = db_models.UserSignIn(**data)

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1_sign_in_unsuccessful(
    user_1_user_id: str,
) -> tuple[models.UserSignIn, db_models.UserSignIn, ModelData]:
    r"""An unsuccessful passkey sign in for test user 1.

    Returns
    -------
    model : streamlit_passwordless.models.UserSignIn
        The model of the user sign in.

    db_model : streamlit_passwordless.database.models.UserSignIn
        The database model of the user sign in.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'user_sign_in_id': 2,
        'user_id': user_1_user_id,
        'sign_in_timestamp': datetime(2003, 8, 26, 13, 37, 37, tzinfo=TZ_UTC),
        'success': False,
        'origin': 'https://ax7.com/',
        'device': 'Firefox',
        'country': 'SE',
        'credential_nickname': 'afterlife',
        'credential_id': 'credential_id_2',
        'sign_in_type': 'passkey_register',
        'rp_id': 'critical_acclaim',
    }

    model = models.UserSignIn.model_validate(data)
    db_model = db_models.UserSignIn(**data)

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1(user_1_user_id: str) -> tuple[models.User, db_models.User, ModelData]:
    r"""Test user 1 without emails and no passkey sign in.

    Returns
    -------
    model : streamlit_passwordless.models.User
        The model of the user.

    db_model : streamlit_passwordless.database.models.User
        The database model of the user.

    data : ModelData
        The input data that created `model`.
    """

    user_id = user_1_user_id
    username = 'rev'
    ad_username = 'the.rev'
    displayname = 'Jimmy'
    verified_at = None
    disabled = False
    disabled_timestamp = None

    data = {
        'user_id': user_id,
        'username': username,
        'ad_username': ad_username,
        'displayname': displayname,
        'verified_at': verified_at,
        'disabled': disabled,
        'disabled_timestamp': disabled_timestamp,
        'emails': None,
        'sign_in': None,
        'aliases': None,
    }

    model = models.User.model_validate(data)
    db_model = db_models.User(
        user_id=user_id,
        username=username,
        ad_username=ad_username,
        displayname=displayname,
        verified_at=verified_at,
        disabled=disabled,
        disabled_timestamp=disabled_timestamp,
    )

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1_with_2_emails_and_successful_signin(
    user_1: tuple[models.User, db_models.User, ModelData],
    user_1_email_primary: tuple[models.Email, db_models.Email, ModelData],
    user_1_email_secondary: tuple[models.Email, db_models.Email, ModelData],
    user_1_sign_in_successful: tuple[models.UserSignIn, db_models.UserSignIn, ModelData],
) -> tuple[models.User, db_models.User, ModelData]:
    r"""Test user 1 with two emails and a successful passkey sign in.

    Returns
    -------
    model : streamlit_passwordless.models.User
        The model of the user.

    db_model : streamlit_passwordless.database.models.User
        The database model of the user.

    data : ModelData
        The input data that created `model`.
    """

    email_primary, _, _ = user_1_email_primary
    email_secondary, _, _ = user_1_email_secondary
    _, _, sign_in_data = user_1_sign_in_successful
    _, db_model, user_data = user_1

    data = user_data.copy()
    data['emails'] = [email_primary, email_secondary]
    data['sign_in'] = sign_in_data
    model = models.User.model_validate(data)

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1_with_unsuccessful_signin(
    user_1: tuple[models.User, db_models.User, ModelData],
    user_1_sign_in_unsuccessful: tuple[models.UserSignIn, db_models.UserSignIn, ModelData],
) -> tuple[models.User, db_models.User, ModelData]:
    r"""Test user 1 with no emails and an unsuccessful passkey sign in.

    Returns
    -------
    model : streamlit_passwordless.models.User
        The model of the user.

    db_model : streamlit_passwordless.database.models.User
        The database model of the user.

    data : ModelData
        The input data that created `model`.
    """

    _, _, sign_in_data = user_1_sign_in_unsuccessful
    _, db_model, user_data = user_1

    data = user_data.copy()
    data['sign_in'] = sign_in_data
    model = models.User.model_validate(data)

    return model, db_model, data


@pytest.fixture()
def passwordless_verified_user() -> tuple[VerifiedUser, models.UserSignIn, ModelData]:
    r"""An instance of `passwordless.VerifiedUser`.

    Returns
    -------
    verified_user : passwordless.VerifiedUser
        The verified user instance.

    model : streamlit_passwordless.models.UserSignIn
        The corresponding `UserSignIn` model of `verified_user`.

    data : ModelData
        The input data that created `verified_user`.
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

    user_sign_in = models.UserSignIn(
        user_sign_in_id=None,
        user_id=data['user_id'],
        sign_in_timestamp=data['timestamp'],
        success=data['success'],
        origin=data['origin'],
        device=data['device'],
        country=data['country'],
        credential_nickname=data['nickname'],
        credential_id=data['credential_id'],
        sign_in_type=data['type'],
        rp_id=data['rp_id'],
    )

    return verified_user, user_sign_in, data


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

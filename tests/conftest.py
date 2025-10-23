r"""Fixtures for testing streamlit-passwordless."""

# ruff:  noqa: ARG001

# Standard library
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from unittest.mock import Mock
from uuid import UUID
from zoneinfo import ZoneInfo

# Third party
import pytest
import streamlit as st
from passwordless import VerifiedUser
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from streamlit.testing.v1 import AppTest

# Local
import streamlit_passwordless.bitwarden_passwordless.backend
import streamlit_passwordless.components
from streamlit_passwordless import common, models
from streamlit_passwordless.bitwarden_passwordless import BitwardenPasswordlessClient
from streamlit_passwordless.database import SessionFactory
from streamlit_passwordless.database import models as db_models

from .config import (
    STATIC_FILES_COMPONENTS_APP_MAIN,
    TZ_UTC,
    DbWithCustomRoles,
    DbWithRoles,
    ModelData,
)

# =============================================================================================
# Models
# =============================================================================================


@pytest.fixture
def viewer_role() -> tuple[models.Role, db_models.Role, ModelData]:
    r"""The VIEWER role.

    Returns
    -------
    model : streamlit_passwordless.models.Role
        The model of the VIEWER role.

    db_model : streamlit_passwordless.database.models.Role
        The database model of the VIEWER role.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'role_id': 1,
        'name': db_models.UserRoleName.VIEWER,
        'rank': 1,
        'description': 'A user that can only view data within an application.',
    }
    model = models.Role.model_validate(data)
    db_model = db_models.Role(**data)

    return model, db_model, data


@pytest.fixture
def user_role() -> tuple[models.Role, db_models.Role, ModelData]:
    r"""The USER role.

    Returns
    -------
    model : streamlit_passwordless.models.Role
        The model of the USER role.

    db_model : streamlit_passwordless.database.models.Role
        The database model of the USER role.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'role_id': 2,
        'name': db_models.UserRoleName.USER,
        'rank': 2,
        'description': 'The standard user with normal privileges. The default role for a new user.',
    }
    model = models.Role.model_validate(data)
    db_model = db_models.Role(**data)

    return model, db_model, data


@pytest.fixture
def superuser_role() -> tuple[models.Role, db_models.Role, ModelData]:
    r"""The SUPERUSER role.

    Returns
    -------
    model : streamlit_passwordless.models.Role
        The model of the SUPERUSER role.

    db_model : streamlit_passwordless.database.models.Role
        The database model of the SUPERUSER role.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'role_id': 3,
        'name': db_models.UserRoleName.SUPERUSER,
        'rank': 3,
        'description': (
            'A user with higher privileges that can perform certain '
            'operations that a normal `USER` can not.'
        ),
    }
    model = models.Role.model_validate(data)
    db_model = db_models.Role(**data)

    return model, db_model, data


@pytest.fixture
def admin_role() -> tuple[models.Role, db_models.Role, ModelData]:
    r"""The ADMIN role.

    Returns
    -------
    model : streamlit_passwordless.models.Role
        The model of the ADMIN role.

    db_model : streamlit_passwordless.database.models.Role
        The database model of the ADMIN role.

    data : ModelData
        The input data that created `model`.
    """

    data = {
        'role_id': 4,
        'name': db_models.UserRoleName.ADMIN,
        'rank': 4,
        'description': (
            'An admin has full access to everything. Only admin users may sign '
            'in to the admin page and manage the users of the application. '
            'An application should have at least one admin.'
        ),
    }
    model = models.Role.model_validate(data)
    db_model = db_models.Role(**data)

    return model, db_model, data


@pytest.fixture
def drummer_custom_role() -> tuple[models.CustomRole, db_models.CustomRole, ModelData]:
    r"""The role of a user that is a drummer.

    Returns
    -------
    model : streamlit_passwordless.CustomRole
        The model of the drummer role.

    db_model : streamlit_passwordless.db.models.CustomRole
        The database model of the drummer role.

    data : dict[str, Any]
        The input data that created `model`.
    """

    data = {
        'role_id': 1,
        'name': 'Drummer',
        'rank': 4,
        'description': 'An epic drummer worthy of playing Beast and the Harlot super drum solo.',
    }
    model = models.CustomRole.model_validate(data)
    db_model = db_models.CustomRole(**data)

    return model, db_model, data


@pytest.fixture
def guitarist_custom_role() -> tuple[models.CustomRole, db_models.CustomRole, ModelData]:
    r"""The role of a user that is a guitarist.

    Returns
    -------
    model : streamlit_passwordless.CustomRole
        The model of the guitarist role.

    db_model : streamlit_passwordless.db.models.CustomRole
        The database model of the guitarist role.

    data : dict[str, Any]
        The input data that created `model`.
    """

    data = {
        'role_id': 2,
        'name': 'Guitarist',
        'rank': 4,
        'description': 'An epic guitarist worthy of playing the legendary M.I.A solo.',
    }
    model = models.CustomRole.model_validate(data)
    db_model = db_models.CustomRole(**data)

    return model, db_model, data


@pytest.fixture(scope='session')
def user_1_user_id() -> UUID:
    r"""The user ID for test user 1 of the test suite."""

    return UUID('24ba6b71-a766-4bf7-82e5-1f0ae16eeb5b')


@pytest.fixture
def user_1_email_primary(user_1_user_id: UUID) -> tuple[models.Email, db_models.Email, ModelData]:
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
        'email_id': None,
        'user_id': user_1_user_id,
        'email': 'rev@ax7.com',
        'rank': 1,
        'verified': True,
        'verified_at': datetime(1999, 1, 1, 1, 1, 1),
        'disabled': False,
        'disabled_at': None,
    }

    model = models.Email.model_validate(data)
    db_model = db_models.Email(**data)

    return model, db_model, data


@pytest.fixture
def user_1_email_secondary(user_1_user_id: UUID) -> tuple[models.Email, db_models.Email, ModelData]:
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
        'email_id': None,
        'user_id': user_1_user_id,
        'email': 'the.rev@ax7.com',
        'rank': 2,
        'verified': False,
        'verified_at': None,
        'disabled': True,
        'disabled_at': datetime(2007, 10, 30, 12, 0, 0),
    }

    model = models.Email.model_validate(data)
    db_model = db_models.Email(**data)

    return model, db_model, data


@pytest.fixture
def user_1_sign_in_successful(
    user_1_user_id: UUID,
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


@pytest.fixture
def user_1_sign_in_unsuccessful(
    user_1_user_id: UUID,
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


@pytest.fixture
def user_1(
    user_1_user_id: UUID,
    superuser_role: tuple[models.Role, db_models.Role, ModelData],
    drummer_custom_role: tuple[models.CustomRole, db_models.CustomRole, ModelData],
) -> tuple[models.User, db_models.User, ModelData]:
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

    _, db_superuser_role_model, role_data = superuser_role
    _, db_drummer_custom_role_model, custom_role_data = drummer_custom_role
    user_id = user_1_user_id
    username = 'rev'
    ad_username = 'the.rev'
    displayname = 'Jimmy'
    verified = True
    verified_at = None
    disabled = False
    disabled_at = None

    data: dict[str, Any] = {
        'user_id': user_id,
        'username': username,
        'ad_username': ad_username,
        'displayname': displayname,
        'verified': verified,
        'verified_at': verified_at,
        'disabled': disabled,
        'disabled_at': disabled_at,
        'role': role_data,
        'custom_roles': {db_drummer_custom_role_model.role_id: custom_role_data},
        'emails': [],
        'sign_in': None,
        'aliases': None,
    }

    model = models.User.model_validate(data)
    db_model = db_models.User(
        user_id=user_id,
        username=username,
        ad_username=ad_username,
        displayname=displayname,
        role_id=db_superuser_role_model.role_id,
        verified=verified,
        verified_at=verified_at,
        disabled=disabled,
        disabled_at=disabled_at,
        role=db_superuser_role_model,
        custom_roles={db_drummer_custom_role_model.role_id: db_drummer_custom_role_model},
    )

    return model, db_model, data


@pytest.fixture
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

    email_primary, email_primary_db, email_primary_data = user_1_email_primary
    email_secondary, email_secondary_db, email_secondary_data = user_1_email_secondary
    sign_in, sign_in_db, sign_in_data = user_1_sign_in_successful
    user_model, user_model_db, user_data = user_1

    user_model.emails = [email_primary, email_secondary]
    user_model.sign_in = sign_in
    user_model_db.emails = [email_primary_db, email_secondary_db]
    user_model_db.sign_ins = [sign_in_db]

    user_data['emails'] = [email_primary_data, email_secondary_data]
    user_data['sign_in'] = sign_in_data

    return user_model, user_model_db, user_data


@pytest.fixture
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


@pytest.fixture
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
        'user_id': 'c1c77594-39d3-46e6-a17e-89251cd256bb',
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


@pytest.fixture
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


# =============================================================================================
# Database
# =============================================================================================


@pytest.fixture
def empty_sqlite_in_memory_database() -> Generator[tuple[Session, SessionFactory]]:
    r"""An empty in-memory SQLite database.

    The database has all tables created and foreign key constraints enabled.

    Yields
    ------
    session : sqlalchemy.orm.Session
        An open session to the database.

    session_factory : sqlalchemy.orm.sessionmaker
        The session factory that can produce new database sessions.
    """

    engine = create_engine(url='sqlite://', echo=True)
    session_factory = sessionmaker(bind=engine)
    db_models.Base.metadata.create_all(bind=engine)

    with session_factory() as session:
        session.execute(text('PRAGMA foreign_keys=ON'))
        session.commit()
        yield session, session_factory


@pytest.fixture
def sqlite_in_memory_database_with_roles(
    empty_sqlite_in_memory_database: tuple[Session, SessionFactory],
) -> DbWithRoles:
    r"""A SQLite database with roles defined.

    The database has all tables created and foreign key constraints enabled.

    Returns
    -------
    session : sqlalchemy.orm.Session
        An open session to the database.

    session_factory : sqlalchemy.orm.sessionmaker
        The session factory that can produce new database sessions.

    roles : tuple[Role, Role, Role, Role]
        The roles that exist in the database.
    """

    session, session_factory = empty_sqlite_in_memory_database

    roles = (
        db_models.Role(role_id=1, name='Viewer', rank=1, description='A viewer.'),
        db_models.Role(role_id=2, name='User', rank=2),
        db_models.Role(role_id=3, name='SuperUser', rank=3),
        db_models.Role(role_id=4, name='Admin', rank=4, description='An admin.'),
    )

    session.add_all(roles)
    session.commit()

    return session, session_factory, roles


@pytest.fixture
def sqlite_in_memory_database_with_custom_roles(
    sqlite_in_memory_database_with_roles: DbWithRoles,
    drummer_custom_role: tuple[models.CustomRole, db_models.CustomRole, ModelData],
    guitarist_custom_role: tuple[models.CustomRole, db_models.CustomRole, ModelData],
) -> DbWithCustomRoles:
    r"""A SQLite database with roles and custom roles defined.

    The database has all tables created and foreign key constraints enabled.

    Returns
    -------
    session : sqlalchemy.orm.Session
        An open session to the database.

    session_factory : sqlalchemy.orm.sessionmaker
        The session factory that can produce new database sessions.

    roles : tuple[streamlit_passwordless.db.models.CustomRole, streamlit_passwordless.db.models.CustomRole]
        The custom roles that exist in the database.
    """

    session, session_factory, _ = sqlite_in_memory_database_with_roles

    _, _, drummer_data = drummer_custom_role
    _, _, guitarist_data = guitarist_custom_role
    custom_roles = (db_models.CustomRole(**drummer_data), db_models.CustomRole(**guitarist_data))

    session.add_all(custom_roles)
    session.commit()

    return session, session_factory, custom_roles


@pytest.fixture
def sqlite_in_memory_database_with_user(
    empty_sqlite_in_memory_database: tuple[Session, SessionFactory],
    user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
) -> tuple[Session, SessionFactory, db_models.User]:
    r"""A SQLite database with a user with a role, custom roles and emails.

    The database has all tables created and foreign key constraints enabled.

    Returns
    -------
    session : sqlalchemy.orm.Session
        An open session to the database.

    session_factory : sqlalchemy.orm.sessionmaker
        The session factory that can produce new database sessions.

    db_user : streamlit_passwordless.db.models.User
        The user that exists in the database.
    """

    session, session_factory = empty_sqlite_in_memory_database
    _, db_user, _ = user_1_with_2_emails_and_successful_signin

    session.add(db_user.role)
    session.add_all(r for r in db_user.custom_roles.values())
    session.add_all(db_user.emails)
    session.add_all(db_user.sign_ins)
    session.add(db_user)
    session.commit()

    return session, session_factory, db_user


@pytest.fixture
def sqlite_db_with_user(
    tmp_path: Path,
    viewer_role: tuple[models.Role, db_models.Role, ModelData],
    user_role: tuple[models.Role, db_models.Role, ModelData],
    superuser_role: tuple[models.Role, db_models.Role, ModelData],
    admin_role: tuple[models.Role, db_models.Role, ModelData],
    user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
) -> Generator[tuple[Session, SessionFactory, db_models.User]]:
    r"""A file based SQLite database with a roles and a user with custom roles and emails.

    The database has all tables created and foreign key constraints enabled.

    Returns
    -------
    session : sqlalchemy.orm.Session
        An open session to the database.

    session_factory : sqlalchemy.orm.sessionmaker
        The session factory that can produce new database sessions.

    db_user : streamlit_passwordless.db.models.User
        The user that exists in the database.
    """

    db = tmp_path / 'streamlit_passwordless.db'

    engine = create_engine(url=f'sqlite:///{db}', echo=False)
    session_factory = sessionmaker(bind=engine)
    db_models.Base.metadata.create_all(bind=engine)

    _, db_viewer_role, _ = viewer_role
    _, db_user_role, _ = user_role
    _, db_superuser_role, _ = superuser_role
    _, db_admin_role, _ = admin_role
    _, db_user, _ = user_1_with_2_emails_and_successful_signin

    with session_factory() as session:
        session.execute(text('PRAGMA foreign_keys=ON'))
        session.add_all((db_viewer_role, db_user_role, db_superuser_role, db_admin_role))
        session.add_all(r for r in db_user.custom_roles.values())
        session.add(db_user)
        session.commit()

        yield session, session_factory, db_user


# =============================================================================================
# Bitwarden Passwordless
# =============================================================================================


@pytest.fixture
def mocked_bwp_register_button_success(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""A mocked version of the Bitwarden Passwordless register button.

    When the button is clicked a successful registration is performed.
    """

    def mocked_register_button(
        register_token: str,
        public_key: str,
        credential_nickname: str,
        disabled: bool = False,
        label: str = 'Register',
        button_type: Literal['primary', 'secondary'] = 'primary',
        key: str | None = None,
    ) -> tuple[str, dict | None, bool]:
        if st.button(label=label, type=button_type, key=key, disabled=disabled):
            return ('register_token', None, True)

        return ('', None, False)

    monkeypatch.setattr(
        streamlit_passwordless.components.register_form, 'register_button', mocked_register_button
    )


@pytest.fixture
def mocked_bwp_sign_in_button_success(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""A mocked version of the Bitwarden Passwordless sign in button.

    When the button is clicked a successful sign in is performed.
    """

    def mocked_signed_in_button(
        public_key: str,
        alias: str | None = None,
        with_discoverable: bool = True,
        with_autofill: bool = False,
        disabled: bool = False,
        label: str = 'Sign in',
        button_type: Literal['primary', 'secondary'] = 'primary',
        key: str | None = None,
    ) -> tuple[str, dict | None, bool]:
        if st.button(label=label, type=button_type, key=key, disabled=disabled):
            return ('sign_in_token', None, True)

        return ('', None, False)

    monkeypatch.setattr(
        streamlit_passwordless.components.sign_in, 'sign_in_button', mocked_signed_in_button
    )


@pytest.fixture
def bwp_client_with_successful_sign_in(
    user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
) -> tuple[Mock, models.UserSignIn]:
    r"""A Bitwarden Passwordless client that can yield a successful user sign in.

    Returns
    -------
    client : unitest.mock.Mock
        A mocked version of :class:`streamlit_passwordless.BitwardenPasswordlessClient`.

    user_sign_in : streamlit_passwordless.UserSignIn
        The user sign in object generated when the user signs in through the mocked `client`.
    """

    user, _, _ = user_1_with_2_emails_and_successful_signin
    user_sign_in = models.UserSignIn(
        user_id=user.user_id,
        sign_in_timestamp=datetime(2025, 10, 17, 13, 37, 37),
        success=True,
        origin='https://ax7.com',
        device='My device',
        country='SE',
        credential_nickname='nickname',
        credential_id='credential_id',
        sign_in_type='type',
        rp_id='rp_id',
    )

    client = Mock(
        spec_set=BitwardenPasswordlessClient(public_key='public_key', private_key='private_key'),
        name='mocked_bitwarden_passwordless_client',
    )
    client.public_key = 'public_key'

    client.verify_sign_in = Mock(
        spec_set=BitwardenPasswordlessClient.verify_sign_in,
        name='mocked_verify_sign_in',
        return_value=user_sign_in,
    )

    return client, user_sign_in


# =============================================================================================
# Components
# =============================================================================================


@pytest.fixture
def app_components() -> AppTest:
    r"""A Streamlit app to test the components of streamlit-passwordless."""

    return AppTest.from_file(STATIC_FILES_COMPONENTS_APP_MAIN)

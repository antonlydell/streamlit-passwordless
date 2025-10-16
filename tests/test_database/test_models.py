r"""Unit tests for the database models."""

# Standard library
from datetime import datetime

# Third party
import pytest
from sqlalchemy import select
from sqlalchemy.orm import undefer_group

# Local
from streamlit_passwordless import UserID
from streamlit_passwordless.database import models as db_models
from streamlit_passwordless.database.core import Session, SessionFactory
from streamlit_passwordless.database.models import Role
from tests.config import TZ_UTC, DbWithRoles

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture(scope='module')
def updated_at_column() -> tuple[datetime, str]:
    r"""The value for the updated_at column and its iso-formatted string.

    Returns
    -------
    datetime
        The datetime value of the updated_at column.

    str
        The iso-formatted string of the updated_at column.
    """

    return datetime(2024, 10, 16, 18, 31, 31, tzinfo=TZ_UTC), '2024-10-16T18:31:31+00:00'


@pytest.fixture(scope='module')
def created_at_column() -> tuple[datetime, str]:
    r"""The value for the created_at column and its iso-formatted string.

    Returns
    -------
    datetime
        The datetime value of the created_at column.

    str
        The iso-formatted string of the created_at column.
    """

    return datetime(2024, 10, 15, 19, 54, 51, tzinfo=TZ_UTC), '2024-10-15T19:54:51+00:00'


# =============================================================================================
# Tests
# =============================================================================================


class TestRole:
    r"""Tests for the model `Role`."""

    def test_init_with_defaults(self) -> None:
        r"""Test to initialize the model with required parameters only."""

        # Setup
        # ===========================================================
        name = 'VIEWER'
        rank = 1

        # Exercise
        # ===========================================================
        viewer = db_models.Role(name=name, rank=rank)

        # Verify
        # ===========================================================
        assert viewer.role_id is None, 'role_id is incorrect!'
        assert viewer.name == name, 'name is incorrect!'  # type: ignore
        assert viewer.rank == rank, 'rank is incorrect!'
        assert viewer.description is None, 'description is incorrect!'
        assert viewer.updated_at is None, 'updated_at is incorrect!'
        assert viewer.created_at is None, 'created_at is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_init_with_all_parameters(
        self, created_at_column: tuple[datetime, str], updated_at_column: tuple[datetime, str]
    ) -> None:
        r"""Test to supply values for all parameters."""

        # Setup
        # ===========================================================
        role_id = 2
        name = 'USER'
        rank = 2
        description = 'A regular user.'
        updated_at, _ = updated_at_column
        created_at, _ = created_at_column

        # Exercise
        # ===========================================================
        viewer = db_models.Role(
            role_id=role_id,
            name=name,
            rank=rank,
            description=description,
            updated_at=updated_at,
            created_at=created_at,
        )

        # Verify
        # ===========================================================
        assert viewer.role_id == role_id, 'role_id is incorrect!'
        assert viewer.name == name, 'name is incorrect!'
        assert viewer.rank == rank, 'rank is incorrect!'
        assert viewer.description == description, 'description is incorrect!'
        assert viewer.updated_at == updated_at, 'updated_at is incorrect!'
        assert viewer.created_at == created_at, 'created_at is incorrect!'

        # Clean up - None
        # ===========================================================

    def test__repr__(
        self, created_at_column: tuple[datetime, str], updated_at_column: tuple[datetime, str]
    ) -> None:
        r"""Test the `__repr__` method."""

        # Setup
        # ===========================================================
        role_id = 1
        name = 'ADMIN'
        rank = 4
        description = 'An admin user.'
        updated_at, updated_at_str = updated_at_column
        updated_by = 'user_1'
        created_at, created_at_str = created_at_column
        created_by = 'user_2'

        repr_str_exp = f"""Role(
    role_id={role_id},
    name='{name}',
    rank={rank},
    description='{description}',
    updated_at={updated_at_str},
    updated_by='{updated_by}',
    created_at={created_at_str},
    created_by='{created_by}',
)"""

        admin = db_models.Role(
            role_id=role_id,
            name=name,
            rank=rank,
            description=description,
            updated_at=updated_at,
            updated_by=updated_by,
            created_at=created_at,
            created_by=created_by,
        )

        # Exercise
        # ===========================================================
        result = repr(admin)

        # Verify
        # ===========================================================
        print(f'Result:\n{result}\n')
        print(f'Expected Result:\n{repr_str_exp}')

        assert result == repr_str_exp

        # Clean up - None
        # ===========================================================


class TestCustomRole:
    r"""Tests for the model `CustomRole`."""

    def test__repr__(self) -> None:
        r"""Test the `__repr__` method."""

        # Setup
        # ===========================================================
        role_id = 2
        name = 'CUSTOM'
        rank = 2

        repr_str_exp = f"""CustomRole(
    role_id={role_id},
    name='{name}',
    rank={rank},
    description=None,
    updated_at=None,
    updated_by=None,
    created_at=None,
    created_by=None,
)"""

        custom_role = db_models.CustomRole(role_id=role_id, name=name, rank=rank)

        # Exercise
        # ===========================================================
        result = repr(custom_role)

        # Verify
        # ===========================================================
        print(f'Result:\n{result}\n')
        print(f'Expected Result:\n{repr_str_exp}')

        assert result == repr_str_exp

        # Clean up - None
        # ===========================================================


class TestUser:
    r"""Tests for the model `User`."""

    def test__repr__(
        self, created_at_column: tuple[datetime, str], updated_at_column: tuple[datetime, str]
    ) -> None:
        r"""Test the `__repr__` method."""

        # Setup
        # ===========================================================
        updated_at, updated_at_str = updated_at_column
        created_at, created_at_str = created_at_column
        updated_by = 'user_1'

        repr_str_exp = f"""User(
    user_id='user_id',
    username='username',
    ad_username='ad_username',
    displayname='displayname',
    role_id=1,
    verified=False,
    verified_at=2024-10-19T13:56:56,
    disabled=True,
    disabled_at=2024-10-19T13:59:00,
    updated_at={updated_at_str},
    updated_by='{updated_by}',
    created_at={created_at_str},
    created_by=None,
)"""

        user = db_models.User(
            user_id='user_id',
            username='username',
            ad_username='ad_username',
            displayname='displayname',
            role_id=1,
            verified=False,
            verified_at=datetime(2024, 10, 19, 13, 56, 56),
            disabled=True,
            disabled_at=datetime(2024, 10, 19, 13, 59, 0),
            updated_at=updated_at,
            updated_by=updated_by,
            created_at=created_at,
        )

        # Exercise
        # ===========================================================
        result = repr(user)

        # Verify
        # ===========================================================
        print(f'Result:\n{result}\n')
        print(f'Expected Result:\n{repr_str_exp}')

        assert result == repr_str_exp

        # Clean up - None
        # ===========================================================


class TestEmail:
    r"""Tests for the model `Email`."""

    def test__repr__(self, created_at_column: tuple[datetime, str]) -> None:
        r"""Test the `__repr__` method."""

        # Setup
        # ===========================================================
        created_at, created_at_str = created_at_column

        repr_str_exp = f"""Email(
    email_id=None,
    user_id='user_id',
    email='test@example.com',
    rank=1,
    verified=None,
    verified_at=None,
    disabled=None,
    disabled_at=None,
    updated_at=None,
    updated_by=None,
    created_at={created_at_str},
    created_by=None,
)"""

        email = db_models.Email(
            user_id='user_id', email='test@example.com', rank=1, created_at=created_at
        )

        # Exercise
        # ===========================================================
        result = repr(email)

        # Verify
        # ===========================================================
        print(f'Result:\n{result}\n')
        print(f'Expected Result:\n{repr_str_exp}')

        assert result == repr_str_exp

        # Clean up - None
        # ===========================================================


class TestUserSignIn:
    r"""Tests for the model `UserSignIn`."""

    def test__repr__(self, created_at_column: tuple[datetime, str]) -> None:
        r"""Test the `__repr__` method."""

        # Setup
        # ===========================================================
        created_at, created_at_str = created_at_column

        repr_str_exp = f"""UserSignIn(
    user_sign_in_id=1,
    user_id='user_id',
    sign_in_timestamp=2024-10-20T18:15:00,
    success=True,
    origin='origin',
    device='device',
    country='country',
    credential_nickname='credential_nickname',
    credential_id='credential_id',
    sign_in_type='passkey_signin',
    rp_id='rp_id',
    created_at={created_at_str},
)"""

        user_sign_in = db_models.UserSignIn(
            user_sign_in_id=1,
            user_id='user_id',
            sign_in_timestamp=datetime(2024, 10, 20, 18, 15, 0),
            success=True,
            origin='origin',
            device='device',
            country='country',
            credential_nickname='credential_nickname',
            credential_id='credential_id',
            sign_in_type='passkey_signin',
            rp_id='rp_id',
            created_at=created_at,
        )

        # Exercise
        # ===========================================================
        result = repr(user_sign_in)

        # Verify
        # ===========================================================
        print(f'Result:\n{result}\n')
        print(f'Expected Result:\n{repr_str_exp}')

        assert result == repr_str_exp

        # Clean up - None
        # ===========================================================


class TestAuditColumnsMixin:
    r"""Tests for the model `AuditColumnsMixin`."""

    def test_create_role(
        self,
        empty_sqlite_in_memory_database: tuple[Session, SessionFactory],
        user_1_user_id: UserID,
    ) -> None:
        r"""Test to create a role and validate the audit columns."""

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database
        role = Role(
            role_id=1,
            name='User',
            rank=1,
            created_by=user_1_user_id,
        )
        query = select(Role).options(undefer_group('audit')).where(Role.role_id == role.role_id)
        before_create_role = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        # Exercise
        # ===========================================================
        session.add(role)
        session.commit()

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_role = new_session.scalars(query).one()

        assert db_role is not None, f'Role(role_id={role.role_id}) not found in the database!'

        attributes_to_verify = (
            ('updated_at', None),
            ('updated_by', None),
            ('created_by', user_1_user_id),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(db_role, attr) == exp_value, f'db_role.{attr}  is incorrect!'

        after_create_role = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)
        assert before_create_role <= db_role.created_at <= after_create_role, (
            'db_role.created_at is incorrect!'
        )

        # Clean up - None
        # ===========================================================

    def test_update_role(
        self,
        sqlite_in_memory_database_with_roles: DbWithRoles,
        user_1_user_id: UserID,
    ) -> None:
        r"""Test to update a role and validate the audit columns."""

        # Setup
        # ===========================================================
        session, session_factory, _ = sqlite_in_memory_database_with_roles
        role = session.get(Role, 1)

        assert role is not None, 'Role(role_id=1) was not found in test database!'

        new_role_name = 'updated'
        role.name = new_role_name
        role.updated_by = user_1_user_id
        query = select(Role).options(undefer_group('audit')).where(Role.role_id == role.role_id)
        before_update_role = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        # Exercise
        # ===========================================================
        session.add(role)
        session.commit()

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_role = new_session.scalars(query).one()

        assert db_role is not None, f'Role(role_id={role.role_id}) not found in the database!'

        attributes_to_verify = (
            ('name', new_role_name),
            ('updated_by', user_1_user_id),
            ('created_by', None),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(db_role, attr) == exp_value, f'db_role.{attr}  is incorrect!'

        after_update_role = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        assert db_role.updated_at is not None, 'db_role.updated_at is unspecified!'
        assert before_update_role <= db_role.updated_at <= after_update_role, (
            'db_role.updated_at is incorrect!'
        )
        assert isinstance(db_role.created_at, datetime), (
            'db_role.created_at is not a datetime object!'
        )

        # Clean up - None
        # ===========================================================

r"""Unit tests for the crud operations on the email table stp_email."""

# Standard library
from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

# Third party
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import DetachedInstanceError

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.crud.email import get_email
from streamlit_passwordless.database.models import Email, User
from tests.config import DbWithRoles

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture
def sqlite_in_memory_database_with_user_and_email(
    sqlite_in_memory_database_with_roles: DbWithRoles,
) -> tuple[Session, sessionmaker, User]:
    r"""A SQLite database containing a user with an email."""

    session, session_factory, roles = sqlite_in_memory_database_with_roles
    role = roles[0]

    exp_email = Email(
        email='test@example.com',
        rank=1,
        verified=True,
        verified_at=datetime(2025, 1, 20, 9, 8, 7),
        disabled=1,
        disabled_at=datetime(2025, 2, 22, 13, 37, 37),
        updated_at=datetime(2025, 2, 18, 13, 37, 38),
        created_at=datetime(2025, 1, 1, 0, 0, 0),
    )
    user = User(
        user_id=UUID('794c7257-b185-4d07-be6e-4990c1e94721'),
        username='username',
        role_id=role.role_id,
        emails=[exp_email],
        updated_at=datetime(2024, 7, 17, 13, 37, 37),
        created_at=datetime(2024, 6, 6, 13, 37, 38),
    )

    session.add(user)
    session.add(exp_email)
    session.commit()

    return session, session_factory, user


# =============================================================================================
# Tests
# =============================================================================================


class TestGetEmail:
    r"""Tests for the function `get_email`."""

    def test_get_existing_email(
        self, sqlite_in_memory_database_with_user_and_email: tuple[Session, sessionmaker, User]
    ) -> None:
        r"""Test to get an existing email from the database.

        The user of the email should not be loaded by default.
        """

        # Setup
        # ===========================================================
        _, session_factory, exp_user = sqlite_in_memory_database_with_user_and_email
        exp_email = exp_user.emails[0]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            email = get_email(session=session, email=exp_email.email)

        # Verify
        # ===========================================================
        assert email is not None, 'Expected email was not found!'

        attributes_to_verify = (
            ('email_id', 1),
            ('user_id', exp_user.user_id),
            ('email', exp_email.email),
            ('rank', exp_email.rank),
            ('verified', exp_email.verified),
            ('verified_at', exp_email.verified_at),
            ('disabled', exp_email.disabled),
            ('disabled_at', exp_email.disabled_at),
            ('updated_at', exp_email.updated_at),
            ('created_at', exp_email.created_at),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(email, attr) == exp_value, f'{email.email} : email.{attr} is incorrect!'

        with pytest.raises(DetachedInstanceError):  # Check that the user is not loaded.
            email.user

        # Clean up - None
        # ===========================================================

    def test_get_non_existing_email(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test to get a non-existing email from the database."""

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_in_memory_database_with_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            email = get_email(session=session, email='does not exist')

        # Verify
        # ===========================================================
        assert email is None, 'Unexpected email was found!'

        # Clean up - None
        # ===========================================================

    def test_get_existing_email_load_user_of_email(
        self, sqlite_in_memory_database_with_user_and_email: tuple[Session, sessionmaker, User]
    ) -> None:
        r"""Test to get an existing email from the database.

        The user associated with the email should also be loaded.
        """

        # Setup
        # ===========================================================
        session, session_factory, exp_user = sqlite_in_memory_database_with_user_and_email
        exp_email = exp_user.emails[0]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            email = get_email(session=session, email=exp_email.email, load_user=True)

        # Verify
        # ===========================================================
        assert email is not None, 'Expected email was not found!'
        assert email.user is not None, 'Expected user was not found!'

        email_attributes_to_verify = (
            ('email_id', 1),
            ('user_id', exp_user.user_id),
            ('email', exp_email.email),
            ('rank', exp_email.rank),
            ('verified', exp_email.verified),
            ('verified_at', exp_email.verified_at),
            ('disabled', exp_email.disabled),
            ('disabled_at', exp_email.disabled_at),
            ('updated_at', exp_email.updated_at),
            ('created_at', exp_email.created_at),
        )
        for attr, exp_value in email_attributes_to_verify:
            assert getattr(email, attr) == exp_value, f'{email.email} : email.{attr} is incorrect!'

        user = email.user
        user_attributes_to_verify = (
            ('user_id', exp_user.user_id),
            ('username', exp_user.username),
            ('ad_username', exp_user.ad_username),
            ('displayname', exp_user.displayname),
            ('role_id', exp_user.role_id),
            ('verified_at', exp_user.verified_at),
            ('disabled', exp_user.disabled),
            ('disabled_at', exp_user.disabled_at),
            ('updated_at', exp_user.updated_at),
            ('created_at', exp_user.created_at),
        )
        for attr, exp_value in user_attributes_to_verify:
            assert getattr(user, attr) == exp_value, f'user.{attr} is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_database_error(
        self,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test the error message when a `streamlit_passwordless.DatabaseError` is raised."""

        # Setup
        # ===========================================================
        session, _ = empty_sqlite_in_memory_database

        email = 'test@example.com'
        exp_error_msg = f'Error loading email "{email}" from database!'

        monkeypatch.setattr(
            session, 'scalars', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            get_email(session=session, email=email)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================

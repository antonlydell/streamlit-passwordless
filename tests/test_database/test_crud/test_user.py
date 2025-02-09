r"""Unit tests for the crud operations on the User model."""

# Standard library
from datetime import datetime

# Third party
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions
from streamlit_passwordless.models import Email, Role, User
from tests.config import TZ_UTC, DbWithRoles, ModelData

# =============================================================================================
# Tests
# =============================================================================================


class TestCreateUser:
    r"""Tests for the function `create_user`, which creates a user in the database."""

    def test_create_user(self, sqlite_in_memory_database_with_roles: DbWithRoles) -> None:
        r"""Test to create a user."""

        # Setup
        # ===========================================================
        session, session_factory, exp_roles = sqlite_in_memory_database_with_roles
        exp_role = exp_roles[3]
        user_to_create = User(
            username='username',
            ad_username='ad_username',
            displayname='Displayname',
            verified_at=datetime(2025, 2, 1, 18, 55, 23),
            disabled=True,
            disabled_timestamp=datetime(2025, 2, 1, 19, 56, 0),
            role=Role(role_id=exp_role.role_id, name='', rank=0),
        )
        query = select(db.models.User).where(db.models.User.user_id == user_to_create.user_id)

        # Exercise
        # ===========================================================
        db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_user = new_session.scalars(query).one()

        attributes_to_verify = (
            ('user_id', user_to_create.user_id),
            ('username', user_to_create.username),
            ('ad_username', user_to_create.ad_username),
            ('displayname', user_to_create.displayname),
            ('role_id', exp_role.role_id),
            ('verified_at', user_to_create.verified_at),
            ('disabled', user_to_create.disabled),
            ('disabled_timestamp', user_to_create.disabled_timestamp),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(db_user, attr) == exp_value, f'db_user.{attr}  is incorrect!'

        assert isinstance(db_user.modified_at, datetime), 'modified_at is not a datetime object!'
        assert isinstance(db_user.created_at, datetime), 'created_at is not a datetime object!'

        # Clean up - None
        # ===========================================================

    def test_create_user_without_commit(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test to create a user.

        The user is only added to the session and not committed.
        """

        # Setup
        # ===========================================================
        session, session_factory, exp_roles = sqlite_in_memory_database_with_roles
        exp_role = exp_roles[0]
        user_to_create = User(
            username='username',
            role=Role(role_id=exp_role.role_id, name='', rank=0),
        )
        query = select(db.models.User).where(db.models.User.user_id == user_to_create.user_id)

        # Exercise
        # ===========================================================
        db_user = db.create_user(session=session, user=user_to_create, commit=False)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_user_new = new_session.scalars(query).one_or_none()

            assert db_user_new is None, 'User found in the database!'

        attributes_to_verify = (
            ('user_id', user_to_create.user_id),
            ('username', user_to_create.username),
            ('ad_username', user_to_create.ad_username),
            ('displayname', user_to_create.displayname),
            ('role_id', exp_role.role_id),
            ('verified_at', user_to_create.verified_at),
            ('disabled', user_to_create.disabled),
            ('disabled_timestamp', user_to_create.disabled_timestamp),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(db_user, attr) == exp_value, f'db_user.{attr}  is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_role_id_is_none(self, sqlite_in_memory_database_with_roles: DbWithRoles) -> None:
        r"""Test when the `role_id` of the user's role is None.

        `streamlit_passwordless.DatabaseCreateUserError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        session, _, _ = sqlite_in_memory_database_with_roles
        username = 'username'
        error_msg_exp = (
            f'Cannot create user "{username}" because user.role.role_id is not specified!'
        )
        user_to_create = User(username=username, role=Role(name='SuperUser', rank=0))

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseCreateUserError) as exc_info:
            db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_role_id_not_found_in_db(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test when the `role_id` associated with the user is not found in the database.

        `streamlit_passwordless.DatabaseCreateUserError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        session, _, _ = sqlite_in_memory_database_with_roles
        username = 'username'
        error_msg_exp = (
            f'Unable to save user "{username}" to database! Check the logs for more details.'
        )
        user_to_create = User(username=username, role=Role(role_id=-1, name='SuperUser', rank=0))

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseCreateUserError) as exc_info:
            db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================

    def test_create_user_with_email(
        self,
        user_1_with_2_emails_and_successful_signin: tuple[User, db.models.User, ModelData],
        sqlite_in_memory_database_with_roles: DbWithRoles,
    ) -> None:
        r"""Test to create a user with two email addresses."""

        # Setup
        # ===========================================================
        session, session_factory, exp_roles = sqlite_in_memory_database_with_roles
        user_to_create, _, _ = user_1_with_2_emails_and_successful_signin

        assert user_to_create.emails is not None, 'user_to_create has no emails!'

        nr_emails_exp = len(user_to_create.emails)
        emails_exp = {m.email: m for m in user_to_create.emails}
        exp_role = exp_roles[2]

        query = (
            select(db.models.User)
            .options(selectinload(db.models.User.emails))
            .where(db.models.User.user_id == user_to_create.user_id)
        )

        # Exercise
        # ===========================================================
        db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_user = new_session.scalars(query).one()

        assert (
            len(db_user.emails) == nr_emails_exp
        ), f'User does not have {nr_emails_exp} emails in db!'

        for email_id, db_email in enumerate(db_user.emails, start=1):
            email_exp = emails_exp.get(db_email.email)

            assert email_exp is not None, f'{db_email.email} not among the expected emails!'

            email_attributes_to_verify = (
                ('email_id', email_id),
                ('user_id', user_to_create.user_id),
                ('email', email_exp.email),
                ('rank', email_exp.rank),
                ('verified_at', email_exp.verified_at),
                ('disabled', email_exp.disabled),
                ('disabled_timestamp', email_exp.disabled_timestamp),
            )
            for attr, exp_value in email_attributes_to_verify:
                assert (
                    getattr(db_email, attr) == exp_value
                ), f'{db_email.email} : db_email.{attr} is incorrect!'

        user_attributes_to_verify = (
            ('user_id', user_to_create.user_id),
            ('username', user_to_create.username),
            ('ad_username', user_to_create.ad_username),
            ('displayname', user_to_create.displayname),
            ('role_id', exp_role.role_id),
            ('verified_at', user_to_create.verified_at),
            ('disabled', user_to_create.disabled),
            ('disabled_timestamp', user_to_create.disabled_timestamp),
        )
        for attr, exp_value in user_attributes_to_verify:
            assert getattr(db_user, attr) == exp_value, f'db_user.{attr} is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_create_user_with_2_emails_of_same_rank(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test to create a user with 2 emails of the same rank.

        `streamlit_passwordless.DatabaseCreateUserError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        session, _, _ = sqlite_in_memory_database_with_roles
        username = 'username'
        error_msg_exp = (
            f'Unable to save user "{username}" to database! Check the logs for more details.'
        )
        user_to_create = User(
            username=username,
            role=Role(role_id=1, name='', rank=0),
            emails=[
                Email(email='test@example.com', rank=1),
                Email(email='test2@example.com', rank=1),
            ],
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseCreateUserError) as exc_info:
            db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================

    def test_user_created_at_and_modified_at(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test that the columns `created_at` and `modified_at` are correctly set.

        When creating a new user the columns `created_at` and `modified_at`
        should be set to the UTC timestamp when the record was inserted into the database.
        """

        # Setup
        # ===========================================================
        session, session_factory, _ = sqlite_in_memory_database_with_roles

        user_to_create = User(username='username', role=Role(role_id=1, name='', rank=0))
        query = select(db.models.User).where(db.models.User.user_id == user_to_create.user_id)

        before_create_user = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        # Exercise
        # ===========================================================
        db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        after_create_user = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        with session_factory() as new_session:
            db_user = new_session.scalars(query).one()

        for attr in ('modified_at', 'created_at'):
            assert (
                before_create_user <= getattr(db_user, attr) <= after_create_user
            ), f'db_user.{attr} is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_user_email_created_at_and_modified_at(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test that the columns `created_at` and `modified_at` are correctly set.

        When creating a new email the columns `created_at` and `modified_at`
        should be set to the UTC timestamp when the record was inserted into the database.
        """

        # Setup
        # ===========================================================
        session, session_factory, _ = sqlite_in_memory_database_with_roles

        email = 'test@example.com'
        user_to_create = User(
            username='username',
            role=Role(role_id=1, name='', rank=0),
            emails=[Email(user_id='', email=email, rank=1)],
        )
        query = select(db.models.Email).where(db.models.Email.email == email)

        before_create_user = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        # Exercise
        # ===========================================================
        db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        after_create_user = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        with session_factory() as new_session:
            db_email = new_session.scalars(query).one()

        for attr in ('modified_at', 'created_at'):
            assert (
                before_create_user <= getattr(db_email, attr) <= after_create_user
            ), f'db_email.{attr} is incorrect!'

        # Clean up - None
        # ===========================================================

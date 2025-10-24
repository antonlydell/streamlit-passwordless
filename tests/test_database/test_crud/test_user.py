r"""Unit tests for the crud operations on the User model."""

# Standard library
from datetime import datetime
from typing import TypeAlias, cast
from uuid import UUID

# Third party
import pytest
from sqlalchemy import Engine, inspect, select
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.state import InstanceState

# Local
from streamlit_passwordless import database as db
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.models import User as DbUser
from streamlit_passwordless.models import CustomRole, Email, Role, User
from tests.config import DbWithCustomRoles, DbWithRoles, ModelData
from tests.test_database.helpers import count_queries

CustomRoleMapping: TypeAlias = dict[int, CustomRole]

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
            disabled_at=datetime(2025, 2, 1, 19, 56, 0),
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
            ('disabled_at', user_to_create.disabled_at),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(db_user, attr) == exp_value, f'db_user.{attr}  is incorrect!'

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
            ('disabled_at', user_to_create.disabled_at),
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

        assert len(db_user.emails) == nr_emails_exp, (
            f'User does not have {nr_emails_exp} emails in db!'
        )

        for email_id, db_email in enumerate(db_user.emails, start=1):
            email_exp = emails_exp.get(db_email.email)

            assert email_exp is not None, f'{db_email.email} not among the expected emails!'

            email_attributes_to_verify = (
                ('email_id', email_id),
                ('user_id', user_to_create.user_id),
                ('email', email_exp.email),
                ('rank', email_exp.rank),
                ('verified', email_exp.verified),
                ('verified_at', email_exp.verified_at),
                ('disabled', email_exp.disabled),
                ('disabled_at', email_exp.disabled_at),
            )
            for attr, exp_value in email_attributes_to_verify:
                assert getattr(db_email, attr) == exp_value, (
                    f'{db_email.email} : db_email.{attr} is incorrect!'
                )

        user_attributes_to_verify = (
            ('user_id', user_to_create.user_id),
            ('username', user_to_create.username),
            ('ad_username', user_to_create.ad_username),
            ('displayname', user_to_create.displayname),
            ('role_id', exp_role.role_id),
            ('verified_at', user_to_create.verified_at),
            ('disabled', user_to_create.disabled),
            ('disabled_at', user_to_create.disabled_at),
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

    def test_create_user_with_two_custom_roles(
        self,
        sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles,
        drummer_custom_role: tuple[CustomRole, db.models.CustomRole, ModelData],
        guitarist_custom_role: tuple[CustomRole, db.models.CustomRole, ModelData],
    ) -> None:
        r"""Test to create a user with two custom roles.

        Custom roles of the user that have missing values for the `role_id` parameter
        should be ignored when linking the custom roles to the user in the database.
        """

        # Setup
        # ===========================================================
        session, session_factory, _ = sqlite_in_memory_database_with_custom_roles
        custom_role_1, _, _ = drummer_custom_role
        custom_role_2, _, _ = guitarist_custom_role
        custom_roles_exp = cast(
            CustomRoleMapping,
            {
                custom_role_1.role_id: custom_role_1,
                custom_role_2.role_id: custom_role_2,
            },
        )
        custom_roles = custom_roles_exp | {0: CustomRole(name='test', rank=0)}
        nr_exp_custom_roles = len(custom_roles_exp)
        role_id = 1

        user_to_create = User(
            username='username',
            role=Role(role_id=role_id, name='', rank=0),
            custom_roles=custom_roles,
        )
        query = (
            select(db.models.User)
            .options(selectinload(db.models.User.custom_roles))
            .where(db.models.User.user_id == user_to_create.user_id)
        )

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
            ('role_id', role_id),
            ('verified_at', user_to_create.verified_at),
            ('disabled', user_to_create.disabled),
            ('disabled_at', user_to_create.disabled_at),
        )
        for attr, exp_value in attributes_to_verify:
            assert getattr(db_user, attr) == exp_value, f'db_user.{attr}  is incorrect!'

        assert len(db_user.custom_roles) == nr_exp_custom_roles, (
            f'User does not have {nr_exp_custom_roles} custom roles in db!'
        )

        for name, db_custom_role in db_user.custom_roles.items():
            custom_role_exp = custom_roles_exp.get(name)

            assert custom_role_exp is not None, (
                f'{db_custom_role.name} not among the expected custom roles!'
            )

            custom_role_attributes_to_verify = (
                ('role_id', custom_role_exp.role_id),
                ('name', custom_role_exp.name),
                ('rank', custom_role_exp.rank),
                ('description', custom_role_exp.description),
            )
            for attr, exp_value in custom_role_attributes_to_verify:
                assert getattr(db_custom_role, attr) == exp_value, (
                    f'{db_custom_role.name} : db_custom_role.{attr} is incorrect!'
                )

        # Clean up - None
        # ===========================================================

    def test_create_user_with_custom_roles_and_custom_roles_missing_in_db(
        self,
        sqlite_in_memory_database_with_roles: DbWithRoles,
        drummer_custom_role: tuple[CustomRole, db.models.CustomRole, ModelData],
        guitarist_custom_role: tuple[CustomRole, db.models.CustomRole, ModelData],
    ) -> None:
        r"""Test to create a user with custom roles.

        The custom roles do not exist in the database and the
        created user should have no custom roles in the database.
        """

        # Setup
        # ===========================================================
        session, session_factory, _ = sqlite_in_memory_database_with_roles
        custom_role_1, _, _ = drummer_custom_role
        custom_role_2, _, _ = guitarist_custom_role
        custom_roles = cast(
            CustomRoleMapping,
            {custom_role_1.role_id: custom_role_1, custom_role_2.role_id: custom_role_2},
        )

        user_to_create = User(
            username='username', role=Role(role_id=1, name='', rank=0), custom_roles=custom_roles
        )
        query = (
            select(db.models.User)
            .options(selectinload(db.models.User.custom_roles))
            .where(db.models.User.user_id == user_to_create.user_id)
        )

        # Exercise
        # ===========================================================
        db.create_user(session=session, user=user_to_create, commit=True)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_user = new_session.scalars(query).one()

        assert not db_user.custom_roles, f'User {user_to_create.username} has custom roles!'

        # Clean up - None
        # ===========================================================

    def test_create_user_with_custom_roles_and_override_them(
        self,
        sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles,
        drummer_custom_role: tuple[CustomRole, db.models.CustomRole, ModelData],
        guitarist_custom_role: tuple[CustomRole, db.models.CustomRole, ModelData],
    ) -> None:
        r"""Test to create a user with two custom roles and override them.

        The `custom_roles` parameter is specified to associate the provided custom
        roles with the user rather than the custom roles defined on the user to create.
        This avoids a database lookup since the custom roles already exist in the session.
        """

        # Setup
        # ===========================================================
        session, session_factory, db_roles = sqlite_in_memory_database_with_custom_roles
        custom_role_1, _, _ = drummer_custom_role
        custom_role_2, _, _ = guitarist_custom_role
        custom_role_exp = db_roles[0]
        custom_roles = cast(
            CustomRoleMapping,
            {custom_role_1.role_id: custom_role_1, custom_role_2.role_id: custom_role_2},
        )

        user_to_create = User(
            username='username',
            role=Role(role_id=1, name='', rank=0),
            custom_roles=custom_roles,
        )
        query = (
            select(db.models.User)
            .options(selectinload(db.models.User.custom_roles))
            .where(db.models.User.user_id == user_to_create.user_id)
        )

        # Exercise
        # ===========================================================
        db.create_user(
            session=session, user=user_to_create, custom_roles=(custom_role_exp,), commit=True
        )

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_user = new_session.scalars(query).one()

        assert len(db_user.custom_roles) == 1, 'User does not have 1 custom role in db!'

        db_custom_role = db_user.custom_roles.get(custom_role_exp.role_id)
        assert db_custom_role is not None, (
            f'Expected custom role {custom_role_exp.name} does not exist!'
        )

        custom_role_attributes_to_verify = (
            ('role_id', custom_role_exp.role_id),
            ('name', custom_role_exp.name),
            ('rank', custom_role_exp.rank),
            ('description', custom_role_exp.description),
        )
        for attr, exp_value in custom_role_attributes_to_verify:
            assert getattr(db_custom_role, attr) == exp_value, (
                f'{db_custom_role.name} : db_custom_role.{attr} is incorrect!'
            )

        # Clean up - None
        # ===========================================================

    def test_username_not_null_constraint(
        self,
        user_1_user_id: UUID,
        sqlite_in_memory_database_with_roles: DbWithRoles,
    ) -> None:
        r"""Test that the username not null constraint is triggered correctly."""

        # Setup
        # ===========================================================
        session, _, exp_roles = sqlite_in_memory_database_with_roles
        exp_role = exp_roles[3]
        user_to_create = db.models.User(
            user_id=user_1_user_id, username=None, role_id=exp_role.role_id
        )
        exp_error_msg = 'NOT NULL constraint failed: stp_user.username'
        session.add(user_to_create)

        # Exercise
        # ===========================================================
        with pytest.raises(IntegrityError) as exc_info:
            session.commit()

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg


class TestGetUserByUserId:
    r"""Tests for the function `get_user_by_user_id`."""

    def test_user_not_found_in_database(
        self,
        empty_sqlite_in_memory_database: tuple[db.Session, db.SessionFactory],
        user_1_user_id: UUID,
    ) -> None:
        r"""Test to load a user that does not exist in the database."""

        # Setup
        # ===========================================================
        _, session_factory = empty_sqlite_in_memory_database

        # Exercise
        # ===========================================================
        with session_factory() as new_session:
            user = db.get_user_by_user_id(session=new_session, user_id=user_1_user_id)

        # Verify
        # ===========================================================
        assert user is None, f'User(user_id={user_1_user_id}) found in the database!'

        # Clean up - None
        # ===========================================================

    def test_load_user_with_audit_columns_deferred(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and verify its attributes.

        The audit columns `updated_at`, `updated_by`, `created_at`, `created_by`
        should be deferred by default and an error should be raised on access.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        user_id = user_exp.user_id

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_id,
                load_role=False,
                load_custom_roles=False,
                load_emails=False,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            assert len(stmts) == 1, 'Incorrect number of SQL queries to load user!'

            attributes_to_verify = (
                ('user_id', user_id),
                ('username', user_exp.username),
                ('ad_username', user_exp.ad_username),
                ('displayname', user_exp.displayname),
                ('role_id', user_exp.role_id),
                ('verified', user_exp.verified),
                ('verified_at', user_exp.verified_at),
                ('disabled', user_exp.disabled),
                ('disabled_at', user_exp.disabled_at),
            )
            for attr, exp_value in attributes_to_verify:
                if attr == 'created_at':
                    assert isinstance(getattr(user, attr), datetime), (
                        'user.created_at is not a datetime object!'
                    )
                else:
                    assert getattr(user, attr) == exp_value, f'user.{attr} is incorrect!'

            for attr in ('updated_at', 'updated_by', 'created_at', 'created_by'):
                with pytest.raises(InvalidRequestError) as exc_info:
                    getattr(user, attr)

                error_msg_exp = f'{user.__class__.__name__}.{attr}'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

        # Clean up - None
        # ===========================================================

    def test_load_role_and_lazy_load_other_attributes(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its role from the database.

        The `role.description`, `custom_roles` or `emails` should be lazy loaded on access.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        role_exp = user_exp.role
        nr_sql_queries_user_and_role = 1
        nr_sql_queries_description = nr_sql_queries_user_and_role + 1
        max_nr_sql_queries = nr_sql_queries_description + 2

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=True,
                load_custom_roles=False,
                load_emails=False,
                raiseload=False,
                defer_role_description=True,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' not in user_state_unloaded, 'role was not eagerly loaded!'
            assert 'custom_roles' in user_state_unloaded, 'custom_role were eagerly loaded!'
            assert 'emails' in user_state_unloaded, 'emails were eagerly loaded!'

            # Role
            role = user.role
            assert len(stmts) == nr_sql_queries_user_and_role, (
                'More than one SQL query emitted for role!'
            )

            role_attributes_to_verify = (
                ('role_id', role_exp.role_id),
                ('name', role_exp.name),
                ('rank', role_exp.rank),
                ('description', role_exp.description),
            )
            for attr, exp_value in role_attributes_to_verify:
                assert getattr(role, attr) == exp_value, (
                    f'{role.name} : db_custom_role.{attr} is incorrect!'
                )
            assert len(stmts) == nr_sql_queries_description, (
                'No SQL query emitted for loading description!'
            )

            # No raiseload
            _ = user.custom_roles
            _ = user.emails

            assert len(stmts) == max_nr_sql_queries, (
                'No SQL queries emitted for loading custom roles and emails!'
            )

        # Clean up - None
        # ===========================================================

    def test_load_role_with_raiseload_and_defer_role_description(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its role from the database.

        An exception should be raised if trying to access the unloaded attributes
        `role.description`, `custom_roles` and `emails`.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        role_exp = user_exp.role
        nr_sql_queries_exp = 1

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=True,
                load_custom_roles=False,
                load_emails=False,
                raiseload=True,
                defer_role_description=True,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' not in user_state_unloaded, 'role was not eagerly loaded!'
            assert 'custom_roles' in user_state_unloaded, 'custom_role were eagerly loaded!'
            assert 'emails' in user_state_unloaded, 'emails were eagerly loaded!'

            # Role
            role = user.role
            assert len(stmts) == nr_sql_queries_exp, 'More than one SQL query emitted for role!'

            role_attributes_to_verify = (
                ('role_id', role_exp.role_id),
                ('name', role_exp.name),
                ('rank', role_exp.rank),
            )
            for attr, exp_value in role_attributes_to_verify:
                assert getattr(role, attr) == exp_value, (
                    f'{role.name} : db_custom_role.{attr} is incorrect!'
                )

            for model, attr in ((role, 'description'), (user, 'custom_roles'), (user, 'emails')):
                with pytest.raises(InvalidRequestError) as exc_info:
                    getattr(model, attr)

                error_msg_exp = f'{model.__class__.__name__}.{attr}'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

            assert len(stmts) == nr_sql_queries_exp, 'More than one SQL query emitted for role!'

        # Clean up - None
        # ===========================================================

    def test_load_role_with_raiseload_and_no_defer_role_description(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its role from the database.

        An exception should be raised if trying to access the unloaded attributes
        `custom_roles` and `emails`.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        role_exp = user_exp.role
        nr_sql_queries_exp = 1

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=True,
                load_custom_roles=False,
                load_emails=False,
                raiseload=True,
                defer_role_description=False,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' not in user_state_unloaded, 'role was not eagerly loaded!'
            assert 'custom_roles' in user_state_unloaded, 'custom_role were eagerly loaded!'
            assert 'emails' in user_state_unloaded, 'emails were eagerly loaded!'

            # Role
            role = user.role
            assert len(stmts) == nr_sql_queries_exp, 'More than one SQL query emitted for role!'

            role_attributes_to_verify = (
                ('role_id', role_exp.role_id),
                ('name', role_exp.name),
                ('rank', role_exp.rank),
                ('description', role_exp.description),
            )
            for attr, exp_value in role_attributes_to_verify:
                assert getattr(role, attr) == exp_value, (
                    f'{role.name} : db_custom_role.{attr} is incorrect!'
                )

            for model, attr in ((user, 'custom_roles'), (user, 'emails')):
                with pytest.raises(InvalidRequestError) as exc_info:
                    getattr(model, attr)

                error_msg_exp = f'{model.__class__.__name__}.{attr}'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

            assert len(stmts) == nr_sql_queries_exp, 'More than one SQL query emitted for role!'

        # Clean up - None
        # ===========================================================

    def test_load_custom_roles_and_lazy_load_other_attributes(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its custom roles from the database.

        The `custom_role.description`, `role` and `emails` should be lazy loaded on access.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        custom_roles_exp = user_exp.custom_roles
        nr_sql_queries_user_and_custom_roles = 2
        nr_sql_queries_descriptions = nr_sql_queries_user_and_custom_roles + len(custom_roles_exp)
        max_nr_sql_queries = nr_sql_queries_descriptions + 2

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=False,
                load_custom_roles=True,
                load_emails=False,
                raiseload=False,
                defer_role_description=True,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' in user_state_unloaded, 'role was eagerly loaded!'
            assert 'custom_roles' not in user_state_unloaded, (
                'custom_roles were not eagerly loaded!'
            )
            assert 'emails' in user_state_unloaded, 'emails were eagerly loaded!'

            # CustomRole
            _ = user.custom_roles
            assert len(stmts) == nr_sql_queries_user_and_custom_roles, (
                f'> {nr_sql_queries_user_and_custom_roles} SQL queries emitted for custom_roles!'
            )

            for role_id, db_custom_role in user.custom_roles.items():
                custom_role_exp = custom_roles_exp.get(role_id)

                assert custom_role_exp is not None, (
                    f'{db_custom_role.name} not among the expected custom roles!'
                )

                custom_role_attributes_to_verify = (
                    ('role_id', custom_role_exp.role_id),
                    ('name', custom_role_exp.name),
                    ('rank', custom_role_exp.rank),
                    ('description', custom_role_exp.description),
                )
                for attr, exp_value in custom_role_attributes_to_verify:
                    assert getattr(db_custom_role, attr) == exp_value, (
                        f'{db_custom_role.name} : db_custom_role.{attr} is incorrect!'
                    )

            assert len(stmts) == nr_sql_queries_descriptions, (
                'No SQL queries emitted for loading custom role descriptions!'
            )

            # No raiseload
            _ = user.role
            _ = user.emails

            assert len(stmts) == max_nr_sql_queries, (
                'No SQL queries emitted for loading role and emails!'
            )

        # Clean up - None
        # ===========================================================

    def test_load_custom_roles_with_raiseload_and_defer_role_description(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its custom roles from the database.

        An exception will be raised if trying to access the unloaded attributes:
        `custom_role.description`, `role` and `emails`.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        custom_roles_exp = user_exp.custom_roles
        max_nr_sql_queries = 2

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=False,
                load_custom_roles=True,
                load_emails=False,
                raiseload=True,
                defer_role_description=True,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' in user_state_unloaded, 'role was eagerly loaded!'
            assert 'custom_roles' not in user_state_unloaded, (
                'custom_roles were not eagerly loaded!'
            )
            assert 'emails' in user_state_unloaded, 'emails were eagerly loaded!'

            # CustomRole
            _ = user.custom_roles
            assert len(stmts) == max_nr_sql_queries, (
                f'> {max_nr_sql_queries=} SQL queries emitted for custom_roles!'
            )

            for role_id, db_custom_role in user.custom_roles.items():
                custom_role_exp = custom_roles_exp.get(role_id)

                assert custom_role_exp is not None, (
                    f'{db_custom_role.name} not among the expected custom roles!'
                )

                custom_role_attributes_to_verify = (
                    ('role_id', custom_role_exp.role_id),
                    ('name', custom_role_exp.name),
                    ('rank', custom_role_exp.rank),
                )
                for attr, exp_value in custom_role_attributes_to_verify:
                    assert getattr(db_custom_role, attr) == exp_value, (
                        f'{db_custom_role.name} : db_custom_role.{attr} is incorrect!'
                    )

                with pytest.raises(InvalidRequestError) as exc_info:
                    _ = db_custom_role.description

                error_msg_exp = f'{db_custom_role.__class__.__name__}.description'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

            for model, attr in ((user, 'role'), (user, 'emails')):
                with pytest.raises(InvalidRequestError) as exc_info:
                    getattr(model, attr)

                error_msg_exp = f'{model.__class__.__name__}.{attr}'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

            assert len(stmts) == max_nr_sql_queries, (
                f'> {max_nr_sql_queries} emitted for loading custom roles!'
            )

        # Clean up - None
        # ===========================================================

    def test_load_custom_roles_with_raiseload_and_no_defer_role_description(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its custom roles from the database.

        An exception will be raised if trying to access the unloaded attributes `role` and `emails`.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        custom_roles_exp = user_exp.custom_roles
        max_nr_sql_queries = 2

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=False,
                load_custom_roles=True,
                load_emails=False,
                raiseload=True,
                defer_role_description=False,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' in user_state_unloaded, 'role was eagerly loaded!'
            assert 'custom_roles' not in user_state_unloaded, (
                'custom_roles were not eagerly loaded!'
            )
            assert 'emails' in user_state_unloaded, 'emails were eagerly loaded!'

            # CustomRole
            custom_roles = user.custom_roles
            assert len(stmts) == max_nr_sql_queries, (
                f'> {max_nr_sql_queries=} SQL queries emitted for custom_roles!'
            )

            for role_id, db_custom_role in custom_roles.items():
                custom_role_exp = custom_roles_exp.get(role_id)

                assert custom_role_exp is not None, (
                    f'{db_custom_role.name} not among the expected custom roles!'
                )

                custom_role_attributes_to_verify = (
                    ('role_id', custom_role_exp.role_id),
                    ('name', custom_role_exp.name),
                    ('rank', custom_role_exp.rank),
                    ('description', custom_role_exp.description),
                )
                for attr, exp_value in custom_role_attributes_to_verify:
                    assert getattr(db_custom_role, attr) == exp_value, (
                        f'{db_custom_role.name} : db_custom_role.{attr} is incorrect!'
                    )

            for model, attr in ((user, 'role'), (user, 'emails')):
                with pytest.raises(InvalidRequestError) as exc_info:
                    getattr(model, attr)

                error_msg_exp = f'{model.__class__.__name__}.{attr}'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

            assert len(stmts) == max_nr_sql_queries, (
                f'> {max_nr_sql_queries} emitted for loading custom roles!'
            )

        # Clean up - None
        # ===========================================================

    def test_load_emails_and_lazy_load_other_attributes(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its enabled emails from the database.

        The disabled secondary email should not be loaded from the database.
        The `role` and `custom_roles` should be lazy loaded on access.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        email_exp = user_exp.emails[0]  # The primary email
        nr_sql_queries_user_and_emails = 2
        max_nr_sql_queries = nr_sql_queries_user_and_emails + 2  # role and custom roles

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=False,
                load_custom_roles=False,
                load_emails=True,
                raiseload=False,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' in user_state_unloaded, 'role was eagerly loaded!'
            assert 'custom_roles' in user_state_unloaded, 'custom_roles were eagerly loaded!'
            assert 'emails' not in user_state_unloaded, 'emails were not eagerly loaded!'

            # emails
            emails = user.emails
            assert len(stmts) == nr_sql_queries_user_and_emails, (
                f'> {nr_sql_queries_user_and_emails} SQL queries emitted for emails!'
            )
            assert len(emails) == 1, 'More emails than the primary email were loaded!'

            email = emails[0]
            email_attributes_to_verify = (
                ('email_id', email_exp.email_id),
                ('email', email_exp.email),
                ('rank', email_exp.rank),
                ('verified', email_exp.verified),
                ('verified_at', email_exp.verified_at),
                ('disabled', email_exp.disabled),
                ('disabled_at', email_exp.disabled_at),
            )
            for attr, exp_value in email_attributes_to_verify:
                assert getattr(email, attr) == exp_value, (
                    f'{email.email} : email.{attr} is incorrect!'
                )

            # No raiseload
            _ = user.role
            _ = user.custom_roles

            assert len(stmts) == max_nr_sql_queries, (
                'No SQL queries emitted for loading role and custom roles'
            )

        # Clean up - None
        # ===========================================================

    def test_load_emails_with_raiseload(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load a user and its enabled emails from the database.

        An exception should be raised if trying to access the unloaded attributes
        `role` and `custom_roles`.
        """

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        email_exp = user_exp.emails[0]
        nr_sql_queries_user_and_emails = 2

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_exp.user_id,
                load_role=False,
                load_custom_roles=False,
                load_emails=True,
                raiseload=True,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert 'role' in user_state_unloaded, 'role was eagerly loaded!'
            assert 'custom_roles' in user_state_unloaded, 'custom_roles were eagerly loaded!'
            assert 'emails' not in user_state_unloaded, 'emails were not eagerly loaded!'

            # emails
            emails = user.emails
            assert len(stmts) == nr_sql_queries_user_and_emails, (
                f'> {nr_sql_queries_user_and_emails=} SQL queries emitted for emails!'
            )
            assert len(emails) == 1, 'More emails than the primary email were loaded!'

            email = emails[0]
            email_attributes_to_verify = (
                ('email_id', email_exp.email_id),
                ('email', email_exp.email),
                ('rank', email_exp.rank),
                ('verified', email_exp.verified),
                ('verified_at', email_exp.verified_at),
                ('disabled', email_exp.disabled),
                ('disabled_at', email_exp.disabled_at),
            )
            for attr, exp_value in email_attributes_to_verify:
                assert getattr(email, attr) == exp_value, (
                    f'{email.email} : email.{attr} is incorrect!'
                )

            for model, attr in ((user, 'role'), (user, 'custom_roles')):
                with pytest.raises(InvalidRequestError) as exc_info:
                    getattr(model, attr)

                error_msg_exp = f'{model.__class__.__name__}.{attr}'
                assert error_msg_exp in exc_info.exconly(), f'{error_msg_exp} not in error message!'

            assert len(stmts) == nr_sql_queries_user_and_emails, (
                f'> {nr_sql_queries_user_and_emails=} emitted!'
            )

        # Clean up - None
        # ===========================================================

    def test_undefer_audit_columns(
        self, sqlite_in_memory_database_with_user: tuple[db.Session, db.SessionFactory, DbUser]
    ) -> None:
        r"""Test to load the, by default, deferred audit columns."""

        # Setup
        # ===========================================================
        _, session_factory, user_exp = sqlite_in_memory_database_with_user
        user_id = user_exp.user_id
        max_nr_sql_queries = 3  # user and role, custom_roles and emails

        # Exercise
        # ===========================================================
        with (
            session_factory() as new_session,
            count_queries(engine=cast(Engine, new_session.get_bind())) as stmts,
        ):
            user = db.get_user_by_user_id(
                session=new_session,
                user_id=user_id,
                load_role=True,
                load_custom_roles=True,
                load_emails=True,
                raiseload=True,
                undefer_audit_columns=True,
            )

            # Verify
            # ===========================================================
            assert user is not None, (
                f'User(username={user_exp.username}) not found in the database!'
            )

            user_state = cast(InstanceState, inspect(user))
            user_state_unloaded = user_state.unloaded

            assert user.role not in user_state_unloaded, 'role was not eagerly loaded!'
            assert 'custom_roles' not in user_state_unloaded, (
                'custom_roles were not eagerly loaded!'
            )
            assert 'emails' not in user_state_unloaded, 'emails were not eagerly loaded!'

            emails = user.emails
            assert len(emails) == 1, 'More emails than the primary email were loaded!'

            custom_roles = list(user.custom_roles.values())
            assert len(custom_roles) == 1, 'The number of loaded custom roles are incorrect!'

            attributes_to_verify = ('updated_by', 'updated_at', 'created_by', 'created_at')
            for obj in (user, user.role, emails[0], custom_roles[0]):
                name = obj.__class__.__name__
                for attr in attributes_to_verify:
                    if attr == 'created_at':
                        assert isinstance(getattr(obj, attr), datetime), (
                            f'{name}.created_at is not a datetime object!'
                        )
                    else:
                        assert getattr(obj, attr) is None, f'{name}.{attr} is incorrect!'

            assert len(stmts) == max_nr_sql_queries, (
                f'More than {max_nr_sql_queries=} were emitted!'
            )

        # Clean up - None
        # ===========================================================

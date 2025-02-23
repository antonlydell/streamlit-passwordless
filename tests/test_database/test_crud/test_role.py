r"""Unit tests for the crud operations on the Role model."""

# Standard library
from datetime import datetime
from itertools import zip_longest
from unittest.mock import Mock

# Third party
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.crud.role import (
    create_default_roles,
    create_role,
    get_all_roles,
    get_role_by_name,
    get_role_by_role_id,
)
from streamlit_passwordless.database.models import Role
from streamlit_passwordless.database.schemas.role import RoleCreate
from tests.config import DbWithRoles

# =============================================================================================
# Tests
# =============================================================================================


class TestGetAllRoles:
    r"""Tests for the function `get_all_roles`."""

    def test_get_all_roles(self, sqlite_in_memory_database_with_roles: DbWithRoles) -> None:
        r"""Test to get all roles from the database."""

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_all_roles(session=session)

        # Verify
        # ===========================================================
        assert not isinstance(roles, pd.DataFrame), 'roles should be list[Role]!'  # type: ignore

        for exp, role in zip_longest(exp_roles, roles):
            assert exp.role_id == role.role_id, 'name attribute is incorrect!'
            assert exp.name == role.name, 'name attribute is incorrect!'
            assert exp.rank == role.rank, 'rank attribute is incorrect!'
            assert exp.description == role.description, 'description attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_get_all_roles_as_dataframe(
        self, sqlite_in_memory_database_with_roles: DbWithRoles
    ) -> None:
        r"""Test to get all roles from the database as a `pandas.DataFrame`."""

        # Setup
        # ===========================================================
        _, session_factory, roles = sqlite_in_memory_database_with_roles

        role_1, role_2 = roles[1], roles[2]
        df_exp = pd.DataFrame(
            data={
                'role_id': [role_1.role_id, role_2.role_id],
                'name': [role_1.name, role_2.name],
                'rank': [role_1.rank, role_2.rank],
                'description': [role_1.description, role_2.description],
            }
        ).set_index('role_id')

        # Exercise
        # ===========================================================
        with session_factory() as session:
            df = get_all_roles(session=session, skip=1, limit=2, as_df=True)

        # Verify
        # ===========================================================
        assert isinstance(df, pd.DataFrame), 'df is not a pandas.DataFrame!'
        assert_frame_equal(df.loc[:, ['name', 'rank', 'description']], df_exp)

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

        exp_error_msg = 'Error loading roles from database!'
        monkeypatch.setattr(
            session, 'scalars', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            get_all_roles(session=session)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================


class TestGetRoleByName:
    r"""Tests for the function `get_role_by_name`."""

    def test_get_existing_role_by_name(
        self, sqlite_in_memory_database_with_roles: tuple[Session, sessionmaker, tuple[Role, ...]]
    ) -> None:
        r"""Test to get an existing role by its name from the database."""

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_roles
        exp_role = exp_roles[3]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            role = get_role_by_name(session=session, name=exp_role.name)

        # Verify
        # ===========================================================
        assert role is not None, 'Expected role was not found!'
        assert exp_role.role_id == role.role_id, 'name attribute is incorrect!'
        assert exp_role.name == role.name, 'name attribute is incorrect!'
        assert exp_role.rank == role.rank, 'rank attribute is incorrect!'
        assert exp_role.description == role.description, 'description attribute is incorrect!'
        assert isinstance(exp_role.modified_at, datetime), 'modified_at is not a datetime object!'
        assert isinstance(exp_role.created_at, datetime), 'created_at is not a datetime object!'

        # Clean up - None
        # ===========================================================

    def test_get_non_existing_role_by_name(
        self, sqlite_in_memory_database_with_roles: tuple[Session, sessionmaker, tuple[Role, ...]]
    ) -> None:
        r"""Test to get a non-existing role by its name from the database."""

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_in_memory_database_with_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            role = get_role_by_name(session=session, name='does not exist')

        # Verify
        # ===========================================================
        assert role is None, 'Unexpected role was found!'

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

        exp_error_msg = "Error loading role by name='User' from database!"
        monkeypatch.setattr(
            session, 'scalars', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            get_role_by_name(session=session, name='User')

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================


class TestGetRoleByRoleId:
    r"""Tests for the function `get_role_by_role_id`."""

    def test_get_existing_role_by_role_id(
        self, sqlite_in_memory_database_with_roles: tuple[Session, sessionmaker, tuple[Role, ...]]
    ) -> None:
        r"""Test to get an existing role by its `role_id` from the database."""

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_roles
        exp_role = exp_roles[2]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            role = get_role_by_role_id(session=session, role_id=exp_role.role_id)

        # Verify
        # ===========================================================
        assert role is not None, 'Expected role was not found!'
        assert exp_role.role_id == role.role_id, 'role_id attribute is incorrect!'
        assert exp_role.name == role.name, 'name attribute is incorrect!'
        assert exp_role.rank == role.rank, 'rank attribute is incorrect!'
        assert exp_role.description == role.description, 'description attribute is incorrect!'
        assert isinstance(exp_role.modified_at, datetime), 'modified_at is not a datetime object!'
        assert isinstance(exp_role.created_at, datetime), 'created_at is not a datetime object!'

        # Clean up - None
        # ===========================================================

    def test_get_non_existing_role_by_role_id(
        self, sqlite_in_memory_database_with_roles: tuple[Session, sessionmaker, tuple[Role, ...]]
    ) -> None:
        r"""Test to get a non-existing role by its `role_id` from the database."""

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_in_memory_database_with_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            role = get_role_by_role_id(session=session, role_id=-1)

        # Verify
        # ===========================================================
        assert role is None, 'Unexpected role was found!'

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

        exp_error_msg = "Error loading role from database!"
        monkeypatch.setattr(
            session, 'scalars', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            get_role_by_role_id(session=session, role_id=1)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================


class TestCreateRole:
    r"""Tests for the function `create_role`."""

    @pytest.mark.parametrize(
        'role_to_create',
        (
            pytest.param(
                RoleCreate(name='User', rank=2, description='This is a user'), id='with description'
            ),
            pytest.param(RoleCreate(name='Admin', rank=4), id='without description'),
        ),
    )
    def test_create_role_with_commit(
        self,
        role_to_create: RoleCreate,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
    ) -> None:
        r"""Test to create a new role in the database.

        The role is added to the session and committed to the database.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database
        query = select(Role).where(Role.name == role_to_create.name)

        # Exercise
        # ===========================================================
        create_role(session=session, role=role_to_create, commit=True)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            role = new_session.scalars(query).one()

        assert role.role_id == 1, 'role_id attribute is incorrect!'
        assert role.name == role_to_create.name, 'name attribute is incorrect!'
        assert role.rank == role_to_create.rank, 'rank attribute is incorrect!'
        assert role.description == role_to_create.description, 'description attribute is incorrect!'
        assert isinstance(role.modified_at, datetime), 'modified_at is not a datetime object!'
        assert isinstance(role.created_at, datetime), 'created_at is not a datetime object!'

        # Clean up - None
        # ===========================================================

    def test_create_role_without_commit(
        self,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
    ) -> None:
        r"""Test to create a new role in the database.

        The role is only added to the session and not committed.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database
        role_to_create = RoleCreate(name='Admin', rank=4)
        query = select(Role).where(Role.name == role_to_create.name)

        # Exercise
        # ===========================================================
        role = create_role(session=session, role=role_to_create, commit=False)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_role = new_session.scalars(query).one_or_none()

            assert db_role is None, 'Role found in the database!'

        assert role.name == role_to_create.name, 'name attribute is incorrect!'
        assert role.rank == role_to_create.rank, 'rank attribute is incorrect!'
        assert role.description == role_to_create.description, 'description attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_commit_raises_database_error(
        self,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test the error message when an exception is raised while committing."""

        # Setup
        # ===========================================================
        session, _ = empty_sqlite_in_memory_database

        role_to_create = RoleCreate(name='SuperUser', rank=3)
        exp_error_msg = (
            'Unable to save role SuperUser to database! Check the logs for more details.'
        )
        monkeypatch.setattr(
            session, 'commit', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            create_role(session=session, role=role_to_create, commit=True)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================


class TestCreateDefaultRoles:
    r"""Tests for the function `create_default_roles`."""

    get_roles_order_by_rank_query = select(Role).order_by(Role.rank)
    exp_roles = (
        Role(name='Viewer', rank=1),
        Role(name='User', rank=2),
        Role(name='SuperUser', rank=3),
        Role(name='Admin', rank=4),
    )

    def test_create_default_roles_with_commit(
        self, empty_sqlite_in_memory_database: tuple[Session, sessionmaker]
    ) -> None:
        r"""Test to create the default roles of streamlit-passwordless.

        The default roles are added to the session and committed to the database.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database

        # Exercise
        # ===========================================================
        create_default_roles(session=session, commit=True)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            roles = new_session.scalars(self.get_roles_order_by_rank_query)

            for exp_role, role in zip_longest(self.exp_roles, roles):
                assert exp_role.name == role.name, 'name attribute is incorrect!'
                assert exp_role.rank == role.rank, 'rank attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_create_default_roles_without_commit(
        self,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
    ) -> None:
        r"""Test to create the default roles of streamlit-passwordless.

        The default roles are only added to the session and not committed.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database

        # Exercise
        # ===========================================================
        roles = create_default_roles(session=session, commit=False)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            roles_from_db = new_session.scalars(self.get_roles_order_by_rank_query).all()

            assert not roles_from_db, 'Default roles found in the database!'

        for exp, role in zip_longest(self.exp_roles, roles):
            assert exp.name == role.name, 'name attribute is incorrect!'
            assert exp.rank == role.rank, 'rank attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_commit_raises_database_error(
        self,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        r"""Test the error message when an exception is raised while committing."""

        # Setup
        # ===========================================================
        session, _ = empty_sqlite_in_memory_database
        exp_error_msg = (
            'Unable to save default roles: Viewer, User, SuperUser, Admin to the database!\n'
            'Check the logs for more details.'
        )
        monkeypatch.setattr(
            session, 'commit', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            create_default_roles(session=session, commit=True)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================

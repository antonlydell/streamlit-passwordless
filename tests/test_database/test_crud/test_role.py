r"""Unit tests for the crud operations on the Role model."""

# Standard library
from itertools import zip_longest
from typing import Generator, TypeAlias
from unittest.mock import Mock

# Third party
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.crud.role import create_default_roles, get_all_roles
from streamlit_passwordless.database.models import Base, Role
from streamlit_passwordless.database.schemas.role import RoleCreate

SQLiteDbWithRolesType: TypeAlias = tuple[Session, sessionmaker, tuple[Role, Role, Role, Role]]

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture(scope='module')
def sqlite_in_memory_database_with_roles() -> Generator[SQLiteDbWithRolesType, None, None]:
    r"""A SQLite database with roles defined.

    The database has all tables created and foreign key constraints enabled.

    Yields
    ------
    session : sqlalchemy.orm.Session
        An open session to the database.

    session_factory : sqlalchemy.orm.sessionmaker
        The session factory that can produce new database sessions.

    roles : tuple[Role, Role, Role, Role]
        The roles that exist in the database.
    """

    engine = create_engine(url='sqlite://', echo=True)
    session_factory = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    roles = (
        Role(role_id=1, name='Viewer', rank=1, description='A viewer.'),
        Role(role_id=2, name='User', rank=2),
        Role(role_id=3, name='SuperUser', rank=3),
        Role(role_id=4, name='Admin', rank=4, description='An admin.'),
    )

    with session_factory() as session:
        session.execute(text('PRAGMA foreign_keys=ON'))
        session.add_all(roles)
        session.commit()

        yield session, session_factory, roles


# =============================================================================================
# Tests
# =============================================================================================


class TestGetAllRoles:
    r"""Tests for the function `get_all_roles`."""

    def test_get_all_roles(
        self, sqlite_in_memory_database_with_roles: SQLiteDbWithRolesType
    ) -> None:
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
        assert not isinstance(roles, pd.DataFrame), 'roles should be list[Role]!'

        for exp, role in zip_longest(exp_roles, roles):
            assert exp.role_id == role.role_id, 'name attribute is incorrect!'
            assert exp.name == role.name, 'name attribute is incorrect!'
            assert exp.rank == role.rank, 'rank attribute is incorrect!'
            assert exp.description == role.description, 'description attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_get_all_roles_as_dataframe(
        self, sqlite_in_memory_database_with_roles: SQLiteDbWithRolesType
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

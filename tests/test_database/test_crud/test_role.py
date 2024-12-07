r"""Unit tests for the crud operations on the Role model."""

# Standard library
from itertools import zip_longest
from unittest.mock import Mock

# Third party
import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.crud.role import create_default_roles
from streamlit_passwordless.database.models import Role

# =============================================================================================
# Tests
# =============================================================================================


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

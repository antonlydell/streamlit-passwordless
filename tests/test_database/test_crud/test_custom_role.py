r"""Unit tests for the crud operations on the CustomRole database model."""

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
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.database import models as db_models
from streamlit_passwordless.database.crud.custom_role import (
    create_custom_role,
    get_all_custom_roles,
    get_custom_roles,
)
from tests.config import TZ_UTC, DbWithCustomRoles

# =============================================================================================
# Tests
# =============================================================================================


class TestGetAllCustomRoles:
    r"""Tests for the function `get_all_custom_roles`."""

    def test_get_all_custom_roles(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get all custom roles from the database."""

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_custom_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_all_custom_roles(session=session)

        # Verify
        # ===========================================================
        assert not isinstance(roles, pd.DataFrame), 'roles should be list[CustomRole]!'

        for exp, role in zip_longest(exp_roles, roles):
            assert exp.role_id == role.role_id, 'role_id attribute is incorrect!'
            assert exp.name == role.name, 'name attribute is incorrect!'
            assert exp.rank == role.rank, 'rank attribute is incorrect!'
            assert exp.description == role.description, 'description attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_get_all_custom_roles_as_dataframe(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get all custom roles from the database as a `pandas.DataFrame`."""

        # Setup
        # ===========================================================
        _, session_factory, roles = sqlite_in_memory_database_with_custom_roles

        role_1, role_2 = roles[0], roles[1]
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
            df = get_all_custom_roles(session=session, as_df=True)

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

        exp_error_msg = 'Error loading custom roles from database!'
        monkeypatch.setattr(
            session, 'scalars', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            get_all_custom_roles(session=session)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================


class TestGetCustomRoles:
    r"""Tests for the function `get_custom_roles`."""

    def test_get_existing_custom_roles_by_role_id(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get existing custom roles by their `role_ids` from the database."""

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_custom_roles
        role_1, role_2 = exp_roles[0], exp_roles[1]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_custom_roles(session=session, role_ids=(role_1.role_id, role_2.role_id))

        # Verify
        # ===========================================================
        for role, exp_role in zip_longest(roles, exp_roles):
            assert role is not None, 'Expected custom role was not found!'
            assert exp_role.role_id == role.role_id, 'role_id attribute is incorrect!'
            assert exp_role.name == role.name, 'name attribute is incorrect!'
            assert exp_role.rank == role.rank, 'rank attribute is incorrect!'
            assert exp_role.description == role.description, 'description attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_get_custom_role_by_role_id_when_name_is_also_specified(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get existing custom roles by their `role_ids` from the database.

        The `names` parameter is also specified, but the `role_ids` parameter should
        take precedence.
        """

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_custom_roles
        role_1, role_2 = exp_roles[0], exp_roles[1]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_custom_roles(
                session=session,
                role_ids=(role_1.role_id, role_2.role_id),
                names=('does not exist', 'nan'),
            )

        # Verify
        # ===========================================================
        for role, exp_role in zip_longest(roles, exp_roles):
            assert role is not None, 'Expected custom role was not found!'
            assert exp_role.role_id == role.role_id, 'role_id attribute is incorrect!'
            assert exp_role.name == role.name, 'name attribute is incorrect!'
            assert exp_role.rank == role.rank, 'rank attribute is incorrect!'
            assert exp_role.description == role.description, 'description attribute is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_get_non_existing_custom_roles_by_role_ids(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get non-existing custom roles by `role_ids` from the database."""

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_in_memory_database_with_custom_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_custom_roles(session=session, role_ids=[-1])

        # Verify
        # ===========================================================
        assert not roles, 'Unexpected custom roles were found!'

        # Clean up - None
        # ===========================================================

    def test_get_existing_custom_roles_by_names(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get existing custom roles by their names from the database."""

        # Setup
        # ===========================================================
        _, session_factory, exp_roles = sqlite_in_memory_database_with_custom_roles
        exp_role = exp_roles[0]

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_custom_roles(session=session, names=(exp_role.name,))

        # Verify
        # ===========================================================
        role = roles[0]

        assert len(roles) == 1, 'Unexpected custom roles were found!'
        assert role is not None, 'Expected custom role was not found!'
        assert exp_role.role_id == role.role_id, 'role_id attribute is incorrect!'
        assert exp_role.name == role.name, 'name attribute is incorrect!'
        assert exp_role.rank == role.rank, 'rank attribute is incorrect!'
        assert exp_role.description == role.description, 'description attribute is incorrect!'
        assert isinstance(exp_role.modified_at, datetime), 'modified_at is not a datetime object!'
        assert isinstance(exp_role.created_at, datetime), 'created_at is not a datetime object!'

        # Clean up - None
        # ===========================================================

    def test_get_non_existing_custom_roles_by_names(
        self, sqlite_in_memory_database_with_custom_roles: DbWithCustomRoles
    ) -> None:
        r"""Test to get non-existing custom roles by their names from the database."""

        # Setup
        # ===========================================================
        _, session_factory, _ = sqlite_in_memory_database_with_custom_roles

        # Exercise
        # ===========================================================
        with session_factory() as session:
            roles = get_custom_roles(session=session, names=('does not exist', 'nan'))

        # Verify
        # ===========================================================
        assert not roles, 'Unexpected custom roles were found!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_role_ids_and_names_are_none(
        self, empty_sqlite_in_memory_database: tuple[Session, sessionmaker]
    ) -> None:
        r"""The parameters `role_id` and `name` are both set to None.

        `streamlit_passwordless.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        session, _ = empty_sqlite_in_memory_database
        exp_error_msg = 'Either "role_ids" or "names" parameter must be specified!'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            get_custom_roles(session=session)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

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

        exp_error_msg = 'Error loading custom roles from database!'
        monkeypatch.setattr(
            session, 'scalars', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            get_custom_roles(session=session, names=('test',))

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================


class TestCreateCustomRole:
    r"""Tests for the function `create_custom_role`."""

    @pytest.mark.parametrize(
        'role_to_create',
        (
            pytest.param(
                models.CustomRole(role_id=1, name='Drummer', rank=2, description='Epic drummer!'),
                id='with role_id and description',
            ),
            pytest.param(
                models.CustomRole(name='Guitarist', rank=4), id='without role_id and description'
            ),
        ),
    )
    def test_create_role_with_commit(
        self,
        role_to_create: models.CustomRole,
        empty_sqlite_in_memory_database: tuple[Session, sessionmaker],
    ) -> None:
        r"""Test to create a new custom role in the database.

        The custom role is added to the session and committed to the database.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database
        query = select(db_models.CustomRole).where(db_models.CustomRole.name == role_to_create.name)

        # Exercise
        # ===========================================================
        create_custom_role(session=session, role=role_to_create, commit=True)

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

    def test_create_custom_role_without_commit(
        self, empty_sqlite_in_memory_database: tuple[Session, sessionmaker]
    ) -> None:
        r"""Test to create a new custom role in the database.

        The custom role is only added to the session and not committed.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database
        role_to_create = models.CustomRole(name='Drummer', rank=4)
        query = select(db_models.CustomRole).where(db_models.CustomRole.name == role_to_create.name)

        # Exercise
        # ===========================================================
        role = create_custom_role(session=session, role=role_to_create, commit=False)

        # Verify
        # ===========================================================
        with session_factory() as new_session:
            db_role = new_session.scalars(query).one_or_none()

            assert db_role is None, 'Role found in the database!'

        assert role.name == role_to_create.name, 'name attribute is incorrect!'
        assert role.rank == role_to_create.rank, 'rank attribute is incorrect!'
        assert role.description == role_to_create.description, 'description attribute is incorrect!'
        assert role.modified_at is None, 'modified_at is not None!'  # type: ignore
        assert role.created_at is None, 'created_at is not None!'  # type: ignore

        # Clean up - None
        # ===========================================================

    def test_created_at_and_modified_at(
        self, empty_sqlite_in_memory_database: tuple[Session, sessionmaker]
    ) -> None:
        r"""Test that the columns `created_at` and `modified_at` are correctly set.

        When creating a new custom role the columns `created_at` and `modified_at`
        should be set to the UTC timestamp when the record was inserted into the database.
        """

        # Setup
        # ===========================================================
        session, session_factory = empty_sqlite_in_memory_database
        role_to_create = models.CustomRole(name='Drummer', rank=4)
        query = select(db_models.CustomRole).where(db_models.CustomRole.name == role_to_create.name)

        before_create_role = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        # Exercise
        # ===========================================================
        create_custom_role(session=session, role=role_to_create, commit=True)

        # Verify
        # ===========================================================
        after_create_role = datetime.now(tz=TZ_UTC).replace(tzinfo=None, microsecond=0)

        with session_factory() as new_session:
            db_custom_role = new_session.scalars(query).one()

        for attr in ('modified_at', 'created_at'):
            assert (
                before_create_role <= getattr(db_custom_role, attr) <= after_create_role
            ), f'db_custom_role.{attr} is incorrect!'

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

        role_to_create = models.CustomRole(name='Guitarist', rank=3)
        exp_error_msg = (
            'Unable to save custom role "Guitarist" to database! '
            'Check the logs for more details.'
        )
        monkeypatch.setattr(
            session, 'commit', Mock(side_effect=SQLAlchemyError('A mocked error occurred!'))
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.DatabaseError) as exc_info:
            create_custom_role(session=session, role=role_to_create, commit=True)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert exp_error_msg in error_msg

        # Clean up - None
        # ===========================================================

r"""Unit tests for the database models."""

# Standard library
from datetime import datetime

# Third party
import pytest

# Local
from streamlit_passwordless.database import models as db_models
from tests.config import TZ_UTC

# =============================================================================================
# Fixtures
# =============================================================================================


@pytest.fixture(scope='module')
def modified_at_column() -> tuple[datetime, str]:
    r"""The value for the modified_at column and its iso-formatted string.

    Returns
    -------
    datetime
        The datetime value of the modified_at column.

    str
        The iso-formatted string of the modified_at column.
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
        assert viewer.modified_at is None, 'modified_at is incorrect!'
        assert viewer.created_at is None, 'created_at is incorrect!'

        # Clean up - None
        # ===========================================================

    def test_init_with_all_parameters(
        self, created_at_column: tuple[datetime, str], modified_at_column: tuple[datetime, str]
    ) -> None:
        r"""Test to supply values for all parameters."""

        # Setup
        # ===========================================================
        role_id = 2
        name = 'USER'
        rank = 2
        description = 'A regular user.'
        modified_at, _ = modified_at_column
        created_at, _ = created_at_column

        # Exercise
        # ===========================================================
        viewer = db_models.Role(
            role_id=role_id,
            name=name,
            rank=rank,
            description=description,
            modified_at=modified_at,
            created_at=created_at,
        )

        # Verify
        # ===========================================================
        assert viewer.role_id == role_id, 'role_id is incorrect!'
        assert viewer.name == name, 'name is incorrect!'
        assert viewer.rank == rank, 'rank is incorrect!'
        assert viewer.description == description, 'description is incorrect!'
        assert viewer.modified_at == modified_at, 'modified_at is incorrect!'
        assert viewer.created_at == created_at, 'created_at is incorrect!'

        # Clean up - None
        # ===========================================================

    def test__repr__(
        self, created_at_column: tuple[datetime, str], modified_at_column: tuple[datetime, str]
    ) -> None:
        r"""Test the `__repr__` method."""

        # Setup
        # ===========================================================
        role_id = 1
        name = 'ADMIN'
        rank = 4
        description = 'An admin user.'
        modified_at, modified_at_str = modified_at_column
        created_at, created_at_str = created_at_column

        repr_str_exp = f"""Role(
    role_id={role_id},
    name='{name}',
    rank={rank},
    description='{description}',
    modified_at={modified_at_str},
    created_at={created_at_str},
)"""

        admin = db_models.Role(
            role_id=role_id,
            name=name,
            rank=rank,
            description=description,
            modified_at=modified_at,
            created_at=created_at,
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

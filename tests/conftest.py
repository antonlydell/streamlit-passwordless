r"""Fixtures for testing streamlit-passwordless."""

# Standard library
from unittest.mock import Mock

# Third party
import pytest

# Local
from streamlit_passwordless import models

# =============================================================================================
# Models
# =============================================================================================


@pytest.fixture()
def mocked_user_id(monkeypatch: pytest.MonkeyPatch) -> str:
    r"""Mock the user ID that is generated if a user ID is not supplied to the `User` model.

    Returns
    -------
    mocked_user_id : str
        The user_id that is returned from the mock.
    """

    mocked_user_id = 'mocked-user_id'
    monkeypatch.setattr(models.uuid, 'uuid4', Mock(return_value=mocked_user_id))

    return mocked_user_id

r"""Unit tests for the models' module."""

# Standard library
from copy import deepcopy
from datetime import datetime
from typing import Any, ClassVar, Sequence

# Third party
import pytest
from passwordless import VerifiedUser
from pydantic import ValidationError

# Local
from streamlit_passwordless import exceptions, models
from streamlit_passwordless.database import models as db_models

from .config import ModelData

# =============================================================================================
# Tests
# =============================================================================================


class TestBaseRole:
    r"""Tests for the model `BaseRole`."""

    user_role: ClassVar[models.BaseRole] = models.BaseRole(name='User', rank=1)
    admin_role: ClassVar[models.BaseRole] = models.BaseRole(name='Admin', rank=4)

    def test_init_with_defaults(self) -> None:
        r"""Test to initialize the model with required parameters only."""

        # Setup
        # ===========================================================
        input_data = {'name': 'USER', 'rank': 2}

        data_exp = deepcopy(input_data)
        data_exp['role_id'] = None
        data_exp['description'] = None

        # Exercise
        # ===========================================================
        role = models.Role.model_validate(input_data)

        # Verify
        # ===========================================================
        assert role.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_init_with_all_parameters(self) -> None:
        r"""Test to supply values for all parameters."""

        # Setup
        # ===========================================================
        input_data = {'role_id': 1, 'name': 'USER', 'rank': 2, 'description': 'description'}

        # Exercise
        # ===========================================================
        role = models.Role.model_validate(input_data)

        # Verify
        # ===========================================================
        assert role.model_dump() == input_data

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_left, role_right, exp_result',
        (
            pytest.param(user_role, user_role, True, id='True'),
            pytest.param(user_role, admin_role, False, id='False'),
            pytest.param(user_role, 1, True, id='int True'),
            pytest.param(user_role, 2, False, id='int False'),
        ),
    )
    def test___eq__(
        self, role_left: models.BaseRole, role_right: models.BaseRole | int, exp_result: bool
    ) -> None:
        r"""Test the `__eq__` (==) method."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        result = role_left == role_right

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_left, role_right, exp_result',
        (
            pytest.param(user_role, admin_role, True, id='True'),
            pytest.param(user_role, user_role, False, id='False'),
            pytest.param(user_role, 2, True, id='int True'),
            pytest.param(user_role, 1, False, id='int False'),
        ),
    )
    def test___nq__(
        self, role_left: models.BaseRole, role_right: models.BaseRole | int, exp_result: bool
    ) -> None:
        r"""Test the `__nq__` method (!=)."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        result = role_left != role_right

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_left, role_right, exp_result',
        (
            pytest.param(user_role, admin_role, True, id='True'),
            pytest.param(user_role, user_role, False, id='False'),
            pytest.param(user_role, 2, True, id='int True'),
            pytest.param(user_role, 1, False, id='int False'),
        ),
    )
    def test___lt__(
        self, role_left: models.BaseRole, role_right: models.BaseRole | int, exp_result: bool
    ) -> None:
        r"""Test the `__lt__` method (<)."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        result = role_left < role_right

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_left, role_right, exp_result',
        (
            pytest.param(user_role, admin_role, True, id='< True'),
            pytest.param(user_role, user_role, True, id='<= True'),
            pytest.param(admin_role, user_role, False, id='< False'),
            pytest.param(user_role, 2, True, id='< int True'),
            pytest.param(user_role, 1, True, id='<= int True'),
            pytest.param(user_role, 0, False, id='< int False'),
        ),
    )
    def test___le__(
        self, role_left: models.BaseRole, role_right: models.BaseRole | int, exp_result: bool
    ) -> None:
        r"""Test the `__le__` method (<=)."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        result = role_left <= role_right

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_left, role_right, exp_result',
        (
            pytest.param(admin_role, user_role, True, id='True'),
            pytest.param(user_role, admin_role, False, id='False'),
            pytest.param(user_role, 0, True, id='int True'),
            pytest.param(user_role, 1, False, id='int False'),
        ),
    )
    def test___gt__(
        self, role_left: models.BaseRole, role_right: models.BaseRole | int, exp_result: bool
    ) -> None:
        r"""Test the `__gt__` method (>)."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        result = role_left > role_right

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_left, role_right, exp_result',
        (
            pytest.param(admin_role, user_role, True, id='> True'),
            pytest.param(user_role, user_role, True, id='>= True'),
            pytest.param(user_role, admin_role, False, id='> False'),
            pytest.param(user_role, 0, True, id='> int True'),
            pytest.param(user_role, 1, True, id='>= int True'),
            pytest.param(user_role, 2, False, id='> int False'),
        ),
    )
    def test___ge__(
        self, role_left: models.BaseRole, role_right: models.BaseRole | int, exp_result: bool
    ) -> None:
        r"""Test the `__ge__` method (>=)."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        result = role_left >= role_right

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================


class TestRole:
    r"""Tests for the model `Role`."""

    def test_from_db_role(self, user_role: tuple[models.Role, db_models.Role, ModelData]) -> None:
        r"""Test to initialize the model from an instance of `database.models.Role`."""

        # Setup
        # ===========================================================
        _, db_role, role_data = user_role

        # Exercise
        # ===========================================================
        role = models.Role.model_validate(db_role)

        # Verify
        # ===========================================================
        assert role.model_dump() == role_data

        # Clean up - None
        # ===========================================================

    def test_create_viewer(
        self, viewer_role: tuple[models.Role, db_models.Role, ModelData]
    ) -> None:
        r"""Test to create a VIEWER role."""

        # Setup
        # ===========================================================
        _, _, role_data = viewer_role

        # Exercise
        # ===========================================================
        role = models.Role.create_viewer()

        # Verify
        # ===========================================================
        assert role.model_dump() == role_data

        # Clean up - None
        # ===========================================================

    def test_create_user(self, user_role: tuple[models.Role, db_models.Role, ModelData]) -> None:
        r"""Test to create a USER role."""

        # Setup
        # ===========================================================
        _, _, role_data = user_role

        # Exercise
        # ===========================================================
        role = models.Role.create_user()

        # Verify
        # ===========================================================
        assert role.model_dump() == role_data

        # Clean up - None
        # ===========================================================

    def test_create_superuser(
        self, superuser_role: tuple[models.Role, db_models.Role, ModelData]
    ) -> None:
        r"""Test to create a SUPERUSER role."""

        # Setup
        # ===========================================================
        _, _, role_data = superuser_role

        # Exercise
        # ===========================================================
        role = models.Role.create_superuser()

        # Verify
        # ===========================================================
        assert role.model_dump() == role_data

        # Clean up - None
        # ===========================================================

    def test_create_admin(self, admin_role: tuple[models.Role, db_models.Role, ModelData]) -> None:
        r"""Test to create an ADMIN role."""

        # Setup
        # ===========================================================
        _, _, role_data = admin_role

        # Exercise
        # ===========================================================
        role = models.Role.create_admin()

        # Verify
        # ===========================================================
        assert role.model_dump() == role_data

        # Clean up - None
        # ===========================================================

    def test_is_immutable(self) -> None:
        r"""Test that the model is immutable."""

        # Setup
        # ===========================================================
        role = models.Role(name='Immutable', rank=1)

        # Exercise & Verify
        # ===========================================================
        with pytest.raises(ValidationError):
            role.name = 'Mutable'  # type: ignore

        # Clean up - None
        # ===========================================================


class TestCustomRole:
    r"""Tests for the model `CustomRole`."""

    def test_from_db_custom_role(
        self, drummer_custom_role: tuple[models.CustomRole, db_models.CustomRole, ModelData]
    ) -> None:
        r"""Test to initialize the model from an instance of `database.models.CustomRole`."""

        # Setup
        # ===========================================================
        _, db_custom_role, custom_role_data = drummer_custom_role

        # Exercise
        # ===========================================================
        custom_role = models.CustomRole.model_validate(db_custom_role)

        # Verify
        # ===========================================================
        assert custom_role.model_dump() == custom_role_data

        # Clean up - None
        # ===========================================================


class TestEmail:
    r"""Tests for the model `Email`."""

    def test_init_with_defaults(self) -> None:
        r"""Test to initialize the model with required parameters only."""

        # Setup
        # ===========================================================
        input_data = {
            'user_id': 'user_id',
            'email': 'm.shadows@ax7.com',
            'rank': 1,
            'disabled': False,
        }

        data_exp = input_data.copy()
        data_exp['email_id'] = None
        data_exp['verified'] = False
        data_exp['verified_at'] = None
        data_exp['disabled_at'] = None

        # Exercise
        # ===========================================================
        user = models.Email.model_validate(input_data)

        # Verify
        # ===========================================================
        assert user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_init_with_all_parameters(self) -> None:
        r"""Test to supply values for all parameters."""

        # Setup
        # ===========================================================
        input_data = {
            'email_id': 1,
            'user_id': 'user_id',
            'email': 'test@email.com',
            'rank': 3,
            'verified': True,
            'verified_at': '2024-09-17T21:04:05',
            'disabled': True,
            'disabled_at': datetime(2024, 9, 9, 13, 37, 37),
        }

        data_exp = input_data.copy()
        data_exp['verified_at'] = datetime(2024, 9, 17, 21, 4, 5)

        # Exercise
        # ===========================================================
        user = models.Email.model_validate(input_data)

        # Verify
        # ===========================================================
        assert user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_from_db_email(
        self, user_1_email_primary: tuple[models.Email, db_models.Email, ModelData]
    ) -> None:
        r"""Test to initialize the model from an instance of `database.models.Email`."""

        # Setup
        # ===========================================================
        _, db_email, email_data = user_1_email_primary

        # Exercise
        # ===========================================================
        email = models.Email.model_validate(db_email)

        # Verify
        # ===========================================================
        assert email.model_dump() == email_data

        # Clean up - None
        # ===========================================================


class TestUserSignIn:
    r"""Tests for the model `UserSignIn`."""

    def test_init_with_default_values(self) -> None:
        r"""Test to initialize the model with required parameters only."""

        # Setup
        # ===========================================================
        input_data = {
            'user_id': 'user_id',
            'sign_in_timestamp': datetime(2024, 9, 18, 19, 20, 23),
            'success': True,
            'origin': 'origin',
            'device': 'device',
            'country': 'country',
            'credential_nickname': 'credential_nickname',
            'credential_id': 'credential_id',
            'sign_in_type': 'sign_in_type',
        }
        data_exp = input_data.copy()
        data_exp['user_sign_in_id'] = None
        data_exp['rp_id'] = None

        # Exercise
        # ===========================================================
        user_sign_in = models.UserSignIn.model_validate(input_data)

        # Verify
        # ===========================================================
        assert user_sign_in.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_init_with_aliases(self) -> None:
        r"""Test to initialize the model with aliases.

        The following parameters are initialized with their aliases:
        - `sign_in_timestamp`   -> `timestamp`
        - `credential_nickname` -> `nickname`
        - `sign_in_type`        -> `type`
        """

        # Setup
        # ===========================================================
        input_data = {
            'user_sign_in_id': 1,
            'user_id': 'user_id',
            'timestamp': datetime(2024, 9, 18, 19, 20, 23),
            'success': True,
            'origin': 'origin',
            'device': 'device',
            'country': 'country',
            'nickname': 'credential_nickname',
            'credential_id': 'credential_id',
            'type': 'sign_in_type',
            'rp_id': 'rp_id',
        }
        data_exp = {
            'user_sign_in_id': 1,
            'user_id': 'user_id',
            'sign_in_timestamp': datetime(2024, 9, 18, 19, 20, 23),
            'success': True,
            'origin': 'origin',
            'device': 'device',
            'country': 'country',
            'credential_nickname': 'credential_nickname',
            'credential_id': 'credential_id',
            'sign_in_type': 'sign_in_type',
            'rp_id': 'rp_id',
        }

        # Exercise
        # ===========================================================
        user_sign_in = models.UserSignIn.model_validate(input_data)

        # Verify
        # ===========================================================
        assert user_sign_in.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_from_db_user_sign_in(
        self, user_1_sign_in_unsuccessful: tuple[models.UserSignIn, db_models.UserSignIn, ModelData]
    ) -> None:
        r"""Test to initialize the model from an instance of `database.models.UserSignIn`."""

        # Setup
        # ===========================================================
        _, db_user_sign_in, user_sign_in_data = user_1_sign_in_unsuccessful

        # Exercise
        # ===========================================================
        user_sign_in = models.UserSignIn.model_validate(db_user_sign_in)

        # Verify
        # ===========================================================
        assert user_sign_in.model_dump() == user_sign_in_data

        # Clean up - None
        # ===========================================================

    def test_from_bitwarden_passwordless_verified_user(self) -> None:
        r"""Test to initialize the model from an instance of `passwordless.VerifiedUser`."""

        # Setup
        # ===========================================================
        verified_user = VerifiedUser(
            user_id='user_id',
            timestamp=datetime(2024, 9, 18, 19, 20, 23),
            success=False,
            origin='origin',
            device='device',
            country='country',
            nickname='credential_nickname',
            credential_id='credential_id',
            expires_at=datetime(2024, 9, 19, 19, 20, 23),
            token_id='token_id',
            type='sign_in_type',
            rp_id='rp_id',
        )
        data_exp = {
            'user_sign_in_id': None,
            'user_id': 'user_id',
            'sign_in_timestamp': datetime(2024, 9, 18, 19, 20, 23),
            'success': False,
            'origin': 'origin',
            'device': 'device',
            'country': 'country',
            'credential_nickname': 'credential_nickname',
            'credential_id': 'credential_id',
            'sign_in_type': 'sign_in_type',
            'rp_id': 'rp_id',
        }

        # Exercise
        # ===========================================================
        user_sign_in = models.UserSignIn.model_validate(verified_user)

        # Verify
        # ===========================================================
        assert user_sign_in.model_dump() == data_exp

        # Clean up - None
        # ===========================================================


class TestUser:
    r"""Tests for the model `User`."""

    def test_init_with_defaults(
        self, mocked_user_id: str, user_role: tuple[models.Role, db_models.Role, ModelData]
    ) -> None:
        r"""Test to initialize the model with required parameters only.

        By default a user is created with the `models.UserNameRole.USER` role.
        """

        # Setup
        # ===========================================================
        _, _, role_data = user_role

        username = 'm.shadows'
        data_exp: dict[str, Any] = {
            'user_id': mocked_user_id,
            'username': username,
            'ad_username': None,
            'displayname': None,
            'verified': False,
            'verified_at': None,
            'disabled': False,
            'disabled_at': None,
            'role': role_data,
            'custom_roles': {},
            'emails': [],
            'sign_in': None,
            'aliases': None,
        }

        # Exercise
        # ===========================================================
        user = models.User(username=username)

        # Verify
        # ===========================================================
        assert user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_init_with_all_parameters(
        self,
        user_1_email_primary: tuple[models.Email, db_models.Email, ModelData],
        user_1_email_secondary: tuple[models.Email, db_models.Email, ModelData],
        user_1_sign_in_successful: tuple[models.UserSignIn, db_models.UserSignIn, ModelData],
    ) -> None:
        r"""Test supply values for all parameters of the model."""

        # Setup
        # ===========================================================
        _, _, email_primary_data = user_1_email_primary
        _, _, email_secondary_data = user_1_email_secondary
        _, _, sign_in_data = user_1_sign_in_successful

        input_data = {
            'user_id': 'user_id',
            'username': 'username',
            'ad_username': 'ad_username',
            'displayname': 'displayname',
            'verified': False,
            'verified_at': '2024-09-17T20:48:16',
            'disabled': True,
            'disabled_at': '2024-09-18T21:48:16',
            'role': {'role_id': 1, 'name': 'role', 'rank': 1, 'description': None},
            'custom_roles': {
                'custom_role_1': {
                    'role_id': 1,
                    'name': 'custom_role',
                    'rank': 1,
                    'description': 'description',
                },
            },
            'emails': [email_primary_data, email_secondary_data],
            'sign_in': sign_in_data,
            'aliases': 'Matt;Shadows',
        }

        data_exp = deepcopy(input_data)
        data_exp['verified_at'] = datetime(2024, 9, 17, 20, 48, 16)
        data_exp['disabled_at'] = datetime(2024, 9, 18, 21, 48, 16)
        data_exp['aliases'] = ('Matt', 'Shadows')

        # Exercise
        # ===========================================================
        user = models.User.model_validate(input_data)

        # Verify
        # ===========================================================
        assert user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_from_db_user(self, user_1: tuple[models.User, db_models.User, ModelData]) -> None:
        r"""Test to initialize the model from `database.models.User`."""

        # Setup
        # ===========================================================
        _, db_user, user_data = user_1

        data_exp = deepcopy(user_data)
        data_exp['emails'] = []

        # Exercise
        # ===========================================================
        user = models.User.model_validate(db_user)

        # Verify
        # ===========================================================
        assert user.model_dump() == data_exp

        # Clean up - None
        # ===========================================================

    def test_is_authenticated_user_sign_in_none(
        self, user_1: tuple[models.User, db_models.User, ModelData]
    ) -> None:
        r"""Test that a user that is not signed in is not listed as authenticated."""

        # Setup
        # ===========================================================
        user, _, _ = user_1

        # Exercise & Verify
        # ===========================================================
        assert user.is_authenticated is False, 'user.is_authenticated is True!'
        assert user.sign_in is None, 'user.sign_in is not None!'

        # Clean up - None
        # ===========================================================

    def test_is_authenticated_user_sign_in_success_true(
        self,
        user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
    ) -> None:
        r"""Test that a user that successfully signed in with a passkey is authenticated."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_2_emails_and_successful_signin

        # Exercise & Verify
        # ===========================================================
        assert user.is_authenticated is True, 'user.is_authenticated is False!'
        assert getattr(user.sign_in, 'success') is True, 'user.sign_in.success is False!'

        # Clean up - None
        # ===========================================================

    def test_is_authenticated_user_sign_in_success_false(
        self, user_1_with_unsuccessful_signin: tuple[models.User, db_models.User, ModelData]
    ) -> None:
        r"""Test that a user with a failed passkey sign in is not authenticated."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_unsuccessful_signin

        # Exercise & Verify
        # ===========================================================
        assert user.is_authenticated is False, 'user.is_authenticated is True!'
        assert getattr(user.sign_in, 'success') is False, 'user.sign_in.success is True!'

        # Clean up - None
        # ===========================================================

    def test_is_authenticated_user_sign_in_user_id_not_equal_to_user_user_id(
        self, user_1_sign_in_successful: tuple[models.UserSignIn, db_models.UserSignIn, ModelData]
    ) -> None:
        r"""Test comparing `user.user_id` to `user.sign_in.user_id` when checking authentication.

        If `user.user_id` differs from `user.sign_in.user_id` the user should not be
        authenticated. This safe guards against if a `models.UserSignIn` instance for one
        user is accidentally assigned to another user.
        """

        # Setup
        # ===========================================================
        user_sign_in, _, _ = user_1_sign_in_successful
        user = models.User(user_id='user_id_not_equal_user_sign_in_user_id', username='username')
        user.sign_in = user_sign_in

        # Exercise & Verify
        # ===========================================================
        assert user.is_authenticated is False, 'user.is_authenticated is True!'
        assert getattr(user.sign_in, 'success') is True, 'user.sign_in.success is False!'

        # Clean up - None
        # ===========================================================

    def test_get_primary_email(self) -> None:
        r"""Test to get the primary email of the user."""

        # Setup
        # ===========================================================
        exp_email = 'test@example.com'
        user = models.User(
            username='username',
            emails=[
                models.Email(email=exp_email, rank=1),
                models.Email(email='test2@example.com', rank=2),
            ],
        )

        # Exercise & Verify
        # ===========================================================
        assert user.email == exp_email

        # Clean up - None
        # ===========================================================

    def test_get_primary_email_user_has_no_email_addresses(self) -> None:
        r"""Test to get the primary email of the user.

        If the user has no email addresses an empty string should be returned.
        """

        # Setup
        # ===========================================================
        user = models.User(username='username')

        # Exercise & Verify
        # ===========================================================
        assert user.email == ''

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'aliases, aliases_exp',
        (
            pytest.param(None, None, id='None'),
            pytest.param(('Matt', 'Shadows'), ('Matt', 'Shadows'), id="('Matt', 'Shadows')"),
            pytest.param(['Matt', 'Shadows'], ('Matt', 'Shadows'), id="['Matt', 'Shadows']"),
            pytest.param('Matt;Shadows', ('Matt', 'Shadows'), id='Matt;Shadows;'),
            pytest.param('Matt', ('Matt',), id='str'),
            pytest.param('Matt;', ('Matt',), id='Matt;'),
        ),
    )
    def test_aliases(
        self, aliases: str | Sequence[str], aliases_exp: tuple[str, ...] | None
    ) -> None:
        r"""Test to supply different types of aliases."""

        # Setup
        # ===========================================================
        username = 'm.shadows'

        # Exercise
        # ===========================================================
        user = models.User(username=username, aliases=aliases)

        # Verify
        # ===========================================================
        assert user.aliases == aliases_exp

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_username(self) -> None:
        r"""Test supply an invalid username.

        `exceptions.StreamlitPasswordlessError` is expected to be raised.
        """

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.StreamlitPasswordlessError) as exc_info:
            models.User(username=None)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'username' in error_msg, 'username not in error message!'

        # Clean up - None
        # ===========================================================


class TestUserIsAuthorized:
    r"""Tests for the method `User.is_authorized`."""

    @pytest.mark.parametrize(
        'role_as_int', (pytest.param(False, id='Role'), pytest.param(True, id='int'))
    )
    def test_authenticated_and_authorized_superuser_against_user(
        self,
        role_as_int: bool,
        user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
        user_role: tuple[models.Role, db_models.Role, ModelData],
    ) -> None:
        r"""Test that an authenticated superuser is authorized against a user role."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_2_emails_and_successful_signin
        authorized_role, _, _ = user_role
        role: models.Role | int = authorized_role.rank if role_as_int else authorized_role

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=role) is True

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_as_int', (pytest.param(False, id='Role'), pytest.param(True, id='int'))
    )
    def test_authenticated_and_authorized_superuser_against_superuser(
        self,
        role_as_int: bool,
        user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
        superuser_role: tuple[models.Role, db_models.Role, ModelData],
    ) -> None:
        r"""Test that an authenticated superuser is authorized against a superuser role."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_2_emails_and_successful_signin
        authorized_role, _, _ = superuser_role
        role: models.Role | int = authorized_role.rank if role_as_int else authorized_role

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=role) is True

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_as_int', (pytest.param(False, id='Role'), pytest.param(True, id='int'))
    )
    def test_authenticated_and_not_authorized_superuser_against_admin(
        self,
        role_as_int: bool,
        user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
        admin_role: tuple[models.Role, db_models.Role, ModelData],
    ) -> None:
        r"""Test that an authenticated superuser is not authorized against an admin role."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_2_emails_and_successful_signin
        authorized_role, _, _ = admin_role
        role: models.Role | int = authorized_role.rank if role_as_int else authorized_role

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=role) is False

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_as_int', (pytest.param(False, id='Role'), pytest.param(True, id='int'))
    )
    def test_not_authenticated_and_authorized_superuser_against_user(
        self,
        role_as_int: bool,
        user_1_with_unsuccessful_signin: tuple[models.User, db_models.User, ModelData],
        user_role: tuple[models.Role, db_models.Role, ModelData],
    ) -> None:
        r"""Test that a non-authenticated superuser is not authorized against a user role."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_unsuccessful_signin
        authorized_role, _, _ = user_role
        role: models.Role | int = authorized_role.rank if role_as_int else authorized_role

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=role) is False

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_as_int', (pytest.param(False, id='Role'), pytest.param(True, id='int'))
    )
    def test_not_authenticated_and_authorized_superuser_against_superuser(
        self,
        role_as_int: bool,
        user_1_with_unsuccessful_signin: tuple[models.User, db_models.User, ModelData],
        superuser_role: tuple[models.Role, db_models.Role, ModelData],
    ) -> None:
        r"""Test that a non-authenticated superuser is not authorized against a superuser role."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_unsuccessful_signin
        authorized_role, _, _ = superuser_role
        role: models.Role | int = authorized_role.rank if role_as_int else authorized_role

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=role) is False

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'role_as_int', (pytest.param(False, id='Role'), pytest.param(True, id='int'))
    )
    def test_not_authenticated_and_not_authorized_superuser_against_admin(
        self,
        role_as_int: bool,
        user_1_with_unsuccessful_signin: tuple[models.User, db_models.User, ModelData],
        admin_role: tuple[models.Role, db_models.Role, ModelData],
    ) -> None:
        r"""Test that a non-authenticated superuser is not authorized against an admin role."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_unsuccessful_signin
        authorized_role, _, _ = admin_role
        role: models.Role | int = authorized_role.rank if role_as_int else authorized_role

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=role) is False

        # Clean up - None
        # ===========================================================

    def test_authenticated_and_role_is_none(
        self,
        user_1_with_2_emails_and_successful_signin: tuple[models.User, db_models.User, ModelData],
    ) -> None:
        r"""Test that an authenticated user is authorized when `role` parameter is None."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_2_emails_and_successful_signin

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=None) is True

        # Clean up - None
        # ===========================================================

    def test_not_authenticated_and_role_is_none(
        self, user_1_with_unsuccessful_signin: tuple[models.User, db_models.User, ModelData]
    ) -> None:
        r"""Test that a non-authenticated user is not authorized when `role` parameter is None."""

        # Setup
        # ===========================================================
        user, _, _ = user_1_with_unsuccessful_signin

        # Exercise & Verify
        # ===========================================================
        assert user.is_authorized(role=None) is False

        # Clean up - None
        # ===========================================================

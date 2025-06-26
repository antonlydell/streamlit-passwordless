r"""The database functionality of streamlit-passwordless."""

# Local
from . import models
from .cache import create_session_factory_cached, init
from .core import (
    URL,
    Session,
    SessionFactory,
    commit,
    create_db_url,
    create_session_factory,
)
from .crud.custom_role import create_custom_role, get_all_custom_roles, get_custom_roles
from .crud.email import get_email
from .crud.role import (
    create_default_roles,
    create_role,
    get_all_roles,
    get_role_by_name,
    get_role_by_role_id,
)
from .crud.user import (
    create_user,
    get_all_users,
    get_user_by_user_id,
    get_user_by_username,
)
from .crud.user_sign_in import create_user_sign_in
from .schemas.role import RoleCreate
from .schemas.user import UserCreate
from .schemas.user_sign_in import UserSignInCreate

# The Public API
__all__ = [
    'models',
    # cache
    'create_session_factory_cached',
    'init',
    # core
    'URL',
    'Session',
    'SessionFactory',
    'commit',
    'create_db_url',
    'create_session_factory',
    # custom_role
    'create_custom_role',
    'get_all_custom_roles',
    'get_custom_roles',
    # email
    'get_email',
    # role
    'create_default_roles',
    'create_role',
    'get_all_roles',
    'get_role_by_name',
    'get_role_by_role_id',
    # user
    'create_user',
    'get_all_users',
    'get_user_by_user_id',
    'get_user_by_username',
    # user_sign_in
    'create_user_sign_in',
    # schemas
    'RoleCreate',
    'UserCreate',
    'UserSignInCreate',
]

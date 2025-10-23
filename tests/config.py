r"""Configuration for the test suite."""

# Standard library
from pathlib import Path
from typing import Any, NamedTuple, TypeAlias
from zoneinfo import ZoneInfo

# Local
from streamlit_passwordless.database import Session, SessionFactory
from streamlit_passwordless.database.models import CustomRole, Role

ModelData: TypeAlias = dict[str, Any]
DbWithRoles: TypeAlias = tuple[Session, SessionFactory, tuple[Role, Role, Role, Role]]
DbWithCustomRoles: TypeAlias = tuple[Session, SessionFactory, tuple[CustomRole, CustomRole]]

STATIC_FILES_PATH = Path(__file__).parent / 'static_files'
STATIC_FILES_COMPONENTS = STATIC_FILES_PATH / 'components'
STATIC_FILES_COMPONENTS_APP_MAIN = STATIC_FILES_COMPONENTS / 'main.py'
TZ_UTC = ZoneInfo('UTC')


class TestAppPage(NamedTuple):
    r"""The config of a page in the app to test the components of streamlit-passwordless.

    Parameters
    ----------
    name : str
        The name of the page.

    path : str
        The path to the page relative to the entry point of the app.

    title : str
        The title rendered on the page through :func:`streamlit.title`.
    """

    name: str
    path: str
    title: str


class TestAppConfig(NamedTuple):
    r"""The config of the app to test the components of streamlit-passwordless.

    Parameters
    ----------
    admin_page : TestAppPage
        The config of the admin page.

    home_page : TestAppPage
        The config of the home page.

    register_page : TestAppPage
        The config of the register page.

    sign_in_page : TestAppPage
        The config of the sign in page.

    default_page : str
        The relative path to the default page of the app.
    """

    admin_page: TestAppPage
    home_page: TestAppPage
    register_page: TestAppPage
    sign_in_page: TestAppPage
    default_page: str


test_app_config = TestAppConfig(
    admin_page=TestAppPage(name='Admin', path='admin_page.py', title='Admin page'),
    home_page=TestAppPage(name='Home', path='home_page.py', title='Home page'),
    register_page=TestAppPage(name='Register', path='register_page.py', title='Register page'),
    sign_in_page=TestAppPage(name='Sign in', path='sign_in_page.py', title='Sign in page'),
    default_page='sign_in_page.py',
)

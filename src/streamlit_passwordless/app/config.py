r"""The configuration of the Streamlit Passwordless web app."""

# Standard library
from enum import StrEnum

# Local
from streamlit_passwordless.bitwarden_passwordless import (
    BitwardenPasswordlessClient,
    create_bitwarden_passwordless_client,
)
from streamlit_passwordless.components.config import init_session_state
from streamlit_passwordless.config import ConfigManager
from streamlit_passwordless.database import SessionFactory, create_session_factory
from streamlit_passwordless.metadata import __releasedate__, __version__

MAINTAINER_INFO = f"""\
- Maintainer   : [*Anton Lydell*](https://github.com/antonlydell)
- Version      : {__version__}
- Release date : {__releasedate__}"""

APP_HOME_PAGE_URL = 'https://github.com/antonlydell/streamlit-passwordless'
APP_ISSUES_PAGE_URL = 'https://github.com/antonlydell/streamlit-passwordless/issues'


class Pages(StrEnum):
    r"""The pages of the application."""

    ADMIN = 'pages/admin.py'
    INIT = 'pages/init.py'
    SIGN_IN = 'pages/sign_in.py'


def setup(
    create_database: bool = False,
) -> tuple[BitwardenPasswordlessClient, SessionFactory, ConfigManager]:
    r"""Setup the resources needed to run a Streamlit Passwordless application.

    Parameters
    ----------
    create_database : bool, default False
        If True the database tables are created and if False table creation is omitted.

    Returns
    -------
    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.

    session_factory : streamlit_passwordless.db.SessionFactory
        The session factory that can produce new database sessions.

    cm : streamlit_passwordless.ConfigManager
        The loaded configuration of the application.
    """

    init_session_state()
    cm = ConfigManager.load()
    client = create_bitwarden_passwordless_client(
        public_key=cm.bwp_public_key, private_key=cm.bwp_private_key, _url=cm.bwp_url
    )
    session_factory = create_session_factory(url=cm.db_url, create_database=create_database)

    return client, session_factory, cm

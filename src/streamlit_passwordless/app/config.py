r"""The configuration of the Streamlit Passwordless web app."""

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


def setup(
    create_database: bool = False,
) -> tuple[ConfigManager, SessionFactory, BitwardenPasswordlessClient]:
    r"""Setup the resources needed to run a Streamlit Passwordless application.

    Parameters
    ----------
    create_database : bool, default False
        If True the database tables are created and if False table creation is omitted.

    Returns
    -------
    cm : streamlit_passwordless.ConfigManager
        The loaded configuration of the application.

    session_factory : streamlit_passwordless.db.SessionFactory
        The session factory that can produce new database sessions.

    client : streamlit_passwordless.BitwardenPasswordlessClient
        An instance of the Bitwarden Passwordless client to
        communicate with the backend API.
    """

    init_session_state()
    cm = ConfigManager.load()
    session_factory = create_session_factory(url=cm.db_url, create_database=create_database)
    client = create_bitwarden_passwordless_client(
        public_key=cm.bwp_public_key, private_key=cm.bwp_private_key, _url=cm.bwp_url
    )

    return cm, session_factory, client

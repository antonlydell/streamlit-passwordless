r"""The entry point of the initialization page."""

# Standard library
from pathlib import Path

# Third party
import streamlit as st

# Local
from streamlit_passwordless.app.config import (
    APP_HOME_PAGE_URL,
    APP_ISSUES_PAGE_URL,
    MAINTAINER_INFO,
    setup,
)
from streamlit_passwordless.app.controllers.init import controller

INIT_PATH = Path(__file__)

ABOUT = f"""Initialize the database of Streamlit Passwordless and create an admin account.

{MAINTAINER_INFO}
"""


def init_page() -> None:
    r"""Run the initialization page of Streamlit Passwordless."""

    st.set_page_config(
        page_title='Streamlit Passwordless - Initialize',
        page_icon=':sparkles:',
        layout='wide',
        menu_items={
            'Get Help': APP_HOME_PAGE_URL,
            'Report a bug': APP_ISSUES_PAGE_URL,
            'About': ABOUT,
        },
    )
    cm, session_factory, client = setup(create_database=True)

    with session_factory() as session:
        controller(cm=cm, db_session=session, client=client)


if __name__ == '__main__' or __name__ == '__page__':
    init_page()

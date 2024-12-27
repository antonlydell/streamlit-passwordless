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
)
from streamlit_passwordless.app.controllers.init import controller
from streamlit_passwordless.components.config import init_session_state

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

    if not st.session_state:
        init_session_state()

    controller()


if __name__ == '__main__' or __name__ == '__page__':
    init_page()

r"""The entry point of the sign in page."""

# Third party
import streamlit as st

# Local
from streamlit_passwordless.app.config import (
    APP_HOME_PAGE_URL,
    APP_ISSUES_PAGE_URL,
    MAINTAINER_INFO,
    setup,
)
from streamlit_passwordless.app.controllers.sign_in import controller

ABOUT = f"""\
Sign in to the Streamlit Passwordless admin web app.

{MAINTAINER_INFO}
"""


def sign_in_page() -> None:
    r"""Run the sign in page of the Streamlit Passwordless admin app."""

    st.set_page_config(
        page_title='Admin Sign in - Streamlit Passwordless',
        page_icon=':key:',
        layout='centered',
        menu_items={
            'About': ABOUT,
            'Get Help': APP_HOME_PAGE_URL,
            'Report a bug': APP_ISSUES_PAGE_URL,
        },
    )
    client, session_factory, _ = setup()

    with session_factory() as session:
        controller(client=client, db_session=session)


if __name__ == '__main__' or __name__ == '__page__':
    sign_in_page()

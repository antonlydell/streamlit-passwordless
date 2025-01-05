r"""The entry point of the admin page."""

# Third party
import streamlit as st

# Local
from streamlit_passwordless.app.config import (
    APP_HOME_PAGE_URL,
    APP_ISSUES_PAGE_URL,
    MAINTAINER_INFO,
    setup,
)
from streamlit_passwordless.app.controllers.admin import controller

ABOUT = f"""\
The Streamlit Passwordless admin web app.

Manage the users of your application.

{MAINTAINER_INFO}
"""


def admin_page() -> None:
    r"""Run the admin page of the Streamlit Passwordless admin app."""

    st.set_page_config(
        page_title='Admin - Streamlit Passwordless',
        page_icon=':bulb:',
        layout='wide',
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
    admin_page()

r"""The entry point of the admin page."""

# Third party
import streamlit as st

# Local
from streamlit_passwordless.app.config import (
    APP_HOME_PAGE_URL,
    APP_ISSUES_PAGE_URL,
    MAINTAINER_INFO,
    Pages,
    setup,
)
from streamlit_passwordless.app.controllers.admin import controller
from streamlit_passwordless.authorization import authorized
from streamlit_passwordless.models import AdminRole

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


admin_page_authorized = authorized(redirect=Pages.SIGN_IN, role=AdminRole)(admin_page)

if __name__ == '__main__' or __name__ == '__page__':
    admin_page_authorized()

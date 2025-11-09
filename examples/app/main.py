r"""The entry point of the Streamlit Passwordless multi-page demo app."""

import streamlit as st
from _pages import Pages
from components import sidebar

import streamlit_passwordless as stp


def setup() -> None:
    r"""Setup the resources of the application."""

    # Initialize client and database
    client, session_factory, _ = stp.setup(create_database=True)
    st.session_state['client'] = client
    st.session_state['session_factory'] = session_factory
    st.session_state['setup_complete'] = True


def main() -> None:
    r"""The main function to run the page router of the app."""

    if 'setup_complete' not in st.session_state:
        setup()

    authenticated, user = stp.authenticated()

    pages = (
        st.Page(page=Pages.ADMIN, title='Admin', icon='🔐'),
        st.Page(page=Pages.HOME, title='Home', icon='🏠'),
        st.Page(
            page=Pages.REGISTER_AND_SIGN_IN, title='Register and Sign in', icon='👋', default=True
        ),
    )
    page = st.navigation(pages, position='sidebar' if authenticated else 'hidden')

    sidebar(user=user, authenticated=authenticated)

    page.run()


if __name__ == '__main__':
    main()

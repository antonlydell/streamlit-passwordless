r"""The entry point of the Streamlit Passwordless admin app."""

# Standard library
from pathlib import Path

# Third party
import streamlit as st

# Local
from streamlit_passwordless.app.config import Pages

APP_PATH = Path(__file__)


def main() -> None:
    r"""The page router for the Streamlit Passwordless admin app."""

    pages = [
        st.Page(page=Pages.ADMIN, title='Admin', default=True),
        st.Page(page=Pages.SIGN_IN, title='Sign in', url_path='sign_in'),
    ]
    page = st.navigation(pages)
    page.run()


if __name__ == '__main__':
    main()

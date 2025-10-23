r"""The home page of the app to test the components of streamlit-passwordless."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless as stp


@stp.authorized(redirect='sign_in_page.py', role=None)
def home() -> None:
    r"""The home page of the app, which can only be accessed by signed in users."""

    st.title('Home page')


if __name__ in {'__main__', '__page__'}:
    home()

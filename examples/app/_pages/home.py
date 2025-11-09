r"""The home page of the Streamlit Passwordless multi-page demo app."""

import streamlit as st
from _pages import Pages

import streamlit_passwordless as stp


@stp.authorized(redirect=Pages.REGISTER_AND_SIGN_IN, role=None)
def home() -> None:
    r"""The home page of the app, which can only be accessed by signed in users."""

    st.title('Home page')
    st.write('All signed in users can access this page.')


if __name__ in {'__main__', '__page__'}:
    home()

r"""The views of the sign in page."""

# Third party
import streamlit as st


def title() -> None:
    r"""Render the title view of the sign in page."""

    st.title('Admin Console')
    st.subheader('Streamlit Passwordless')

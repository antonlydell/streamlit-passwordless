r"""The views of the admin page."""

# Third party
import streamlit as st


def title() -> None:
    r"""Render the title view of the admin page."""

    st.title('Streamlit Passwordless Admin Console')
    st.divider()

r"""The admin page of the Streamlit Passwordless multi-page demo app."""

import streamlit as st
from _pages import Pages

import streamlit_passwordless as stp


@stp.authorized(redirect=Pages.HOME, role=stp.AdminRole)
def admin() -> None:
    r"""The admin page of the app, which can only be accessed by signed-in admin users."""

    st.title('Admin page')
    st.write('Only signed-in admins can view this page.')


if __name__ in {'__main__', '__page__'}:
    admin()

r"""The admin page of the app to test the components of streamlit-passwordless."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless as stp


@stp.authorized(redirect='sign_in_page.py', role=stp.AdminRole)
def admin() -> None:
    r"""The admin page of the app, which can only be accessed by signed in admin users."""

    st.title('Admin page')


if __name__ in {'__main__', '__page__'}:
    admin()

r"""The entry point of the app to test the components of streamlit-passwordless."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless as stp


def main() -> None:
    r"""The main function to run the page router of the app."""

    if st.session_state.get('client') is None:
        raise stp.StreamlitPasswordlessError(
            'st.session_state must contain a key "client" '
            'with an instance (or mock) of streamlit_passwordless.BitwardenPasswordlessClient!'
        )
    if st.session_state.get('session_factory') is None:
        raise stp.StreamlitPasswordlessError(
            'st.session_state must contain a key "session_factory" '
            'with an instance of streamlit_passwordless.db.SessionFactory!'
        )

    pages = (
        st.Page(page='admin_page.py', title='Admin'),
        st.Page(page='home_page.py', title='Home'),
        st.Page(page='register_page.py', title='Register'),
        st.Page(page='sign_in_page.py', title='Sign in', default=True),
    )
    page = st.navigation(pages)

    sign_out_button_params = st.session_state.get('sign_out_button_params', {})

    with st.sidebar:
        stp.sign_out_button(**sign_out_button_params)

    page.run()


if __name__ == '__main__':
    main()

r"""The register and sign-in page of the Streamlit Passwordless multi-page demo app."""

import streamlit as st
from _pages import Pages

import streamlit_passwordless as stp


def register_and_sign_in() -> None:
    r"""The register and sign in page."""

    st.title('Streamlit Passwordless Demo')

    authenticated, _ = stp.authenticated()
    client = st.session_state['client']
    session_factory = st.session_state['session_factory']

    with session_factory() as session:
        stp.db.init(_session=session)  # create the default roles once on startup

        with st.container(border=True):
            if authenticated:
                stp.bitwarden_register_form_existing_user(
                    client=client, db_session=session, border=False
                )
            else:
                stp.bitwarden_register_form(
                    client=client,
                    db_session=session,
                    with_displayname=True,
                    border=False,
                    redirect=Pages.HOME,
                )
            st.write('Already have an account?')
            stp.bitwarden_sign_in_button(
                client=client, db_session=session, load_emails=True, redirect=Pages.HOME
            )


if __name__ in {'__main__', '__page__'}:
    register_and_sign_in()

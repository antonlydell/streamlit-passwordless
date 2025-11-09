r"""A minimal single-page Streamlit application demonstrating basic passkey registration and sign-in."""

import streamlit as st

import streamlit_passwordless as stp


def main() -> None:
    st.set_page_config(page_title='Streamlit Passwordless', page_icon='✨')
    st.title('Streamlit Passwordless Demo')

    # initialize client and database
    client, session_factory, _ = stp.setup(create_database=True)
    with session_factory() as session:
        stp.db.init(_session=session)  # create the default roles once on startup

        with st.container(border=True):
            stp.bitwarden_register_form(client=client, db_session=session, border=False)
            st.write('Already have an account?')
            stp.bitwarden_sign_in_button(client=client, db_session=session)

    stp.sign_out_button(use_container_width=True)


if __name__ == '__main__':
    main()

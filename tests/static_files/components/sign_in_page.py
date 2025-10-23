r"""The sign in page of the app to test the components of streamlit-passwordless."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless as stp


def sign_in() -> None:
    r"""The sign in page."""

    st.title('Sign in page')

    client = st.session_state['client']
    session_factory = st.session_state['session_factory']

    sign_in_params = st.session_state.get('sign_in_params', {})

    with session_factory() as session:
        user_sign_in_form, success_sign_in_form = stp.bitwarden_sign_in_form(
            client=client, db_session=session, **sign_in_params
        )
        user_sign_in_button, success_sign_in_button = stp.bitwarden_sign_in_button(
            client=client, db_session=session, **sign_in_params
        )

    st.session_state['user_sign_in_form'] = user_sign_in_form
    st.session_state['success_sign_in_form'] = success_sign_in_form

    st.session_state['user_sign_in_button'] = user_sign_in_button
    st.session_state['success_sign_in_button'] = success_sign_in_button


if __name__ in {'__main__', '__page__'}:
    sign_in()

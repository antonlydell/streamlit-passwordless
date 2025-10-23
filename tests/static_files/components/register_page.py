r"""The register page of the app to test the components of streamlit-passwordless."""

# Third party
import streamlit as st

# Local
import streamlit_passwordless as stp


def register() -> None:
    r"""The register page."""

    st.title('Register page')

    client = st.session_state['client']
    session_factory = st.session_state['session_factory']

    register_form_params = st.session_state.get('register_params', {})
    register_form_existing_user_params = st.session_state.get('register_existing_user_params', {})

    with session_factory() as session:
        user_register_form, success_register_form = stp.bitwarden_register_form(
            client=client, db_session=session, **register_form_params
        )
        user_register_form_existing_user, success_register_form_existing_user = (
            stp.bitwarden_register_form_existing_user(
                client=client, db_session=session, **register_form_existing_user_params
            )
        )

    st.session_state['user_register_form'] = user_register_form
    st.session_state['success_register_form'] = success_register_form

    st.session_state['user_register_existing_user_form'] = user_register_form_existing_user
    st.session_state['success_register_existing_user_form'] = success_register_form_existing_user


if __name__ in {'__main__', '__page__'}:
    register()

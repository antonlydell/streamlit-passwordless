r"""An example Streamlit application using streamlit-passwordless."""

# Standard library
import os
from pathlib import Path

# Third party
import dotenv
import streamlit as st

import streamlit_passwordless as stp

# The public and private key are exposed as the env variables PUBLIC_KEY
# and PRIVATE_KEY through the dotenv file ".env" respectively.
DOTENV_FILE = Path.cwd() / '.env'


def main() -> None:
    r"""The main function to run the app."""

    st.title('Streamlit Passwordless Demo')
    st.markdown('## Register and Sign In')

    if not st.session_state:
        stp.init_session_state()  # Initialize the session state needed by streamlit-passwordless.

    dotenv.load_dotenv(DOTENV_FILE)  # Load the public and private key into environment variables.

    try:
        client = stp.BitwardenPasswordlessClient(
            public_key=os.getenv('PUBLIC_KEY'),
            private_key=os.getenv('PRIVATE_KEY'),
        )
    except stp.StreamlitPasswordlessError as e:
        st.error(str(e), icon=stp.ICON_ERROR)
        return

    register_tab, signin_in_tab = st.tabs(['Register', 'Sign in'])
    with register_tab:
        stp.bitwarden_register_form(client=client)
    with signin_in_tab:
        stp.bitwarden_sign_in_form(client=client)


if __name__ == '__main__':
    main()

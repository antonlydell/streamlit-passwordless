**********************
streamlit-passwordless
**********************

|PyPI| |LICENSE|


streamlit-passwordless provides a user model for Streamlit applications based on the Bitwarden
passwordless technology. It allows users to securely authenticate with a Streamlit application
using the passkey FIDO2 and WebAuthn protocols.

The project is under development and not yet ready for production. The library can handle
registering a new user by creating and registring a passkey with the user's device and
letting the user sign in with the passkey. The user model is not fully implemented yet.


Installation
============

streamlit-passwordless is available on `PyPI`_ and can be installed with  `pip`_.

.. _pip: https://pip.pypa.io/en/stable/getting-started/
.. _PyPI: https://pypi.org/project/streamlit-passwordless/


.. code-block:: bash

   $ pip install streamlit-passwordless


License
=======

streamlit-passwordless is distributed under the `MIT-license`_.

.. _MIT-license: https://opensource.org/licenses/mit-license.php


Example
=======

Let's create an example Streamlit app using streamlit-passwordless. First create an account with
`Bitwarden Passwordless.dev`_ and make your *public* and *private* key accessable to your
application e.g. through a ".env" file, which we will use in this example. Create a new virtual
environment and install streamlit-passwordless. `python-dotenv`_ is also installed here to handle
loading the credentials for `Bitwarden Passwordless.dev`_.

.. _Bitwarden Passwordless.dev: https://admin.passwordless.dev/Account/Login
.. _python-dotenv: https://pypi.org/project/python-dotenv/


.. code-block:: bash

   ~ $ mkdir stp_demo && cd stp_demo
   ~/stp_demo $ echo ".env" > .gitignore
   ~/stp_demo $ python -m venv .venv
   ~/stp_demo $ source .venv/bin/activate
   ~/stp_demo (.venv) $ python -m pip install streamlit-passwordless python-dotenv


On Windows you should replace with ``source .venv/bin/activate`` with ``.venv/bin/Activate.ps1``.
The contents of the file *.env* is shown below. Replace ``<PUBLIC_KEY>`` and ``<PRIVATE_KEY>``
with your actual *public* and *private* key from Bitwarden Passwordless.dev. The *private key* is
called *secret key* in Bitwarden Passwordless.dev. Make sure the file *.env* is located in your
working directory *stp_demo*.


.. code-block::

   PUBLIC_KEY=<PUBLIC_KEY>
   PRIVATE_KEY=<PRIVATE_KEY>


Copy the code of the example app below into a file called *app.py* and place it in your
working directory *stp_demo*.


.. code-block:: python

   # app.py

   # Standard library
   import os
   from pathlib import Path

   # Third party
   import dotenv
   import streamlit as st
   import streamlit_passwordless as stp

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


The app first initializes the session state variables needed by streamlit-passwordless.
Then it loads the public and private key from the *.env* file and creates the
``BitwardenPasswordlessClient``, which is used to communicate with Bitwarden Passwordless.dev.
Lastly the forms to *register* and *sign in* are rendered in separate tabs.
Run the example app with the following command:


.. code-block:: bash

   ~/stp_demo (.venv) $ python -m streamlit run app.py

   You can now view your Streamlit app in your browser.

   Local URL: http://localhost:8501


Open the url in your favorite web browser and try it out!


.. |PyPI| image:: https://img.shields.io/pypi/v/streamlit-passwordless?style=plastic
   :alt: PyPI
   :scale: 100%
   :target: https://pypi.org/project/streamlit-passwordless/

.. |LICENSE| image:: https://img.shields.io/pypi/l/streamlit-passwordless?style=plastic
   :alt: PyPI - License
   :scale: 100%
   :target: https://github.com/antonlydell/streamlit-passwordless/blob/main/LICENSE

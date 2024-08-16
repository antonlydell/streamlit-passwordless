streamlit-passwordless
======================

|PyPI| |conda-forge| |conda-forge-platform| |Python| |LICENSE|


streamlit-passwordless provides a user model for Streamlit applications based on the Bitwarden
passwordless technology. It allows users to securely authenticate with a Streamlit application
using the passkey FIDO2 and WebAuthn protocols.

The project is under development and not yet ready for production. The library can handle
registering a new user by creating and registring a passkey with the user's device and
letting the user sign in with the passkey. The user model is not fully implemented yet.

A demo of the project is available at: https://passwordless.streamlit.app


Installation
------------

streamlit-passwordless is available on `PyPI`_ and `conda-forge`_ and can be installed with `pip`_
or `conda`_.

.. _conda: https://docs.conda.io/en/latest/
.. _conda-forge: https://anaconda.org/conda-forge/streamlit_passwordless
.. _pip: https://pip.pypa.io/en/stable/getting-started/
.. _PyPI: https://pypi.org/project/streamlit-passwordless/


Install with pip:

.. code-block:: bash

   $ pip install streamlit-passwordless


Install with conda:

.. code-block:: bash

   $ conda install conda-forge::streamlit_passwordless


License
-------

streamlit-passwordless is distributed under the `MIT-license`_.

.. _MIT-license: https://opensource.org/licenses/mit-license.php


Example
-------

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
   DB_URL = 'sqlite:///streamlit_passwordless.db'

   @st.cache_data
   def create_client(public_key: str, private_key: str) -> stp.BitwardenPasswordlessClient:
      r"""Create the client to connect to Bitwarden Passwordless backend API."""

      return stp.BitwardenPasswordlessClient(public_key=public_key, private_key=private_key)

   def main() -> None:
      r"""The main function to run the app."""

      st.title('Streamlit Passwordless Demo')
      st.markdown('## Register and Sign In')

      if not st.session_state:
         stp.init_session_state()  # Initialize the session state needed by streamlit-passwordless.

      dotenv.load_dotenv(DOTENV_FILE)  # Load the public and private key into environment variables.
      public_key, private_key = os.getenv('PUBLIC_KEY'), os.getenv('PRIVATE_KEY')

      if public_key is None or private_key is None:
         st.error('Public or private key not found in environment!', icon=stp.ICON_ERROR)
         return

      try:
         client = create_client(public_key=public_key, private_key=private_key)
      except stp.StreamlitPasswordlessError as e:
         st.error(str(e), icon=stp.ICON_ERROR)
         return

      session_factory = stp.db.create_session_factory(url=DB_URL)

      with session_factory.begin() as session:
         register_tab, signin_in_tab = st.tabs(['Register', 'Sign in'])
         with register_tab:
            stp.bitwarden_register_form(client=client, db_session=session)
         with signin_in_tab:
            stp.bitwarden_sign_in_form(client=client)


   if __name__ == '__main__':
      main()


The app first initializes the session state variables needed by streamlit-passwordless.
Then it loads the public and private key from the *.env* file and creates the
``BitwardenPasswordlessClient``, which is used to communicate with Bitwarden Passwordless.dev.
The database session factory, needed to connect to the user database, is created from the cached
resource function `create_session_factory`. A SQLite database (streamlit_passwordless.db) located
in the current working directory is used in the example and if it does not exist it will be created.
Lastly the forms to *register* and *sign in* are rendered in separate tabs.
Run the example app with the following command:


.. code-block:: bash

   ~/stp_demo (.venv) $ python -m streamlit run app.py

   You can now view your Streamlit app in your browser.

   Local URL: http://localhost:8501


Open the url in your favorite web browser and try it out!

.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/streamlit_passwordless?style=plastic
   :alt: conda-forge - Version
   :scale: 100%
   :target: https://anaconda.org/conda-forge/streamlit_passwordless


.. |conda-forge-platform| image:: https://img.shields.io/conda/pn/conda-forge/streamlit_passwordless?color=yellowgreen&style=plastic
   :alt: conda-forge - Platform
   :scale: 100%
   :target: https://anaconda.org/conda-forge/streamlit_passwordless


.. |LICENSE| image:: https://img.shields.io/pypi/l/streamlit-passwordless?style=plastic
   :alt: PyPI - License
   :scale: 100%
   :target: https://github.com/antonlydell/streamlit-passwordless/blob/main/LICENSE


.. |PyPI| image:: https://img.shields.io/pypi/v/streamlit-passwordless?style=plastic
   :alt: PyPI
   :scale: 100%
   :target: https://pypi.org/project/streamlit-passwordless/


.. |Python| image:: https://img.shields.io/pypi/pyversions/streamlit-passwordless?style=plastic
   :alt: PyPI - Python Version
   :scale: 100%
   :target: https://pypi.org/project/streamlit-passwordless/

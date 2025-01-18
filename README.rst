streamlit-passwordless
======================

|PyPI| |conda-forge| |conda-forge-platform| |Python| |LICENSE|


streamlit-passwordless provides a user model for Streamlit applications based on the Bitwarden
passwordless.dev technology. It allows users to securely authenticate with a Streamlit application
using passkeys. The project is under development and not ready for production yet.

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
`Bitwarden Passwordless.dev`_ and make your *public* and *private* key accessible to your
application. This can be accomplished through environment variables or the `Streamlit secrets`_.
Create a new virtual environment and install streamlit-passwordless.

.. _Bitwarden Passwordless.dev: https://admin.passwordless.dev/Account/Login
.. _python-dotenv: https://pypi.org/project/python-dotenv/
.. _Streamlit secrets: https://docs.streamlit.io/develop/api-reference/connections/secrets.toml


.. code-block:: bash

   ~ $ mkdir stp_demo && cd stp_demo
   ~/stp_demo $ python -m venv .venv
   ~/stp_demo $ source .venv/bin/activate
   ~/stp_demo (.venv) $ python -m pip install streamlit-passwordless
   ~/stp_demo (.venv) $ mkdir .streamlit && touch .streamlit/secrets.toml


On Windows you should replace with ``source .venv/bin/activate`` with ``.venv/bin/Activate.ps1``.
The contents of the file *~/stp_demo/.streamlit/secrets.toml* is shown below. Replace ``<PUBLIC_KEY>``
and ``<PRIVATE_KEY>`` with your actual *public* and *private* key from Bitwarden Passwordless.dev. The
*private key* is called *secret key* in Bitwarden Passwordless.dev. Alternatively you can set the
environment variables `STP_BWP_PUBLIC_KEY` and `STP_BWP_PRIVATE_KEY` to the values of the *public*
and *private* keys respectively.


.. code-block:: toml

   [streamlit-passwordless]
   STP_BWP_PUBLIC_KEY = '<PUBLIC_KEY>'
   STP_BWP_PRIVATE_KEY = '<PRIVATE_KEY>'


Copy the code of the example app below into a file called *app.py* and place it in your
working directory *stp_demo*.


.. code-block:: python

   # app.py


   import streamlit as st
   import streamlit_passwordless as stp


   def main() -> None:
      r"""The main function to run the app."""

      page_title = 'Streamlit Passwordless Minimal Example'
      st.set_page_config(page_title=page_title)
      st.title(page_title)

      client, session_factory, _ = stp.setup(create_database=True)
      with session_factory() as session:
         stp.db.init(_session=session)
         register_tab, signin_in_tab = st.tabs(['Register', 'Sign in'])
         with register_tab:
            stp.bitwarden_register_form(client=client, db_session=session)
         with signin_in_tab:
            stp.bitwarden_sign_in_form(client=client, db_session=session)

      stp.sign_out_button(use_container_width=True)


   if __name__ == '__main__':
      main()


The ``stp.setup`` function initializes the session state variables needed by streamlit-passwordless,
loads and validates the configuration, creates the ``client`` for communicating with Bitwarden
Passwordless.dev and finally creates the ``session_factory`` for interacting with the user database.
By setting ``create_database=True`` the tables of the database are created. By default a SQLite
database (*streamlit_passwordless.db*) located in the current working directory is used. The database
to use can be specified through the config key or environment variable ``STP_DB_URL``, which takes a
`SQLAlchemy database URL`_.

The function ``stp.db.init`` initializes the database by creating the default user roles. This function
is cached with st.cache_resource_, which makes it only execute once. The database can also be initialized
through the streamlit-passwordless CLI by running the command ``stp run init``. It launches a Streamlit
app that initializes the database and lets you create an admin user for the application. Lastly the forms
to *register* and *sign in* are rendered in separate tabs, and finally the *sign out* button is rendered.

.. _st.cache_resource : https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource
.. _SQLAlchemy database URL : https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls


Run the example app with the following command:

.. code-block:: bash

   ~/stp_demo (.venv) $ python -m streamlit run app.py

   You can now view your Streamlit app in your browser.

   Local URL: http://localhost:8501


Open the url in your favorite web browser and try it out!


.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/streamlit_passwordless?style=plastic
   :alt: conda-forge - Version
   :target: https://anaconda.org/conda-forge/streamlit_passwordless


.. |conda-forge-platform| image:: https://img.shields.io/conda/pn/conda-forge/streamlit_passwordless?color=yellowgreen&style=plastic
   :alt: conda-forge - Platform
   :target: https://anaconda.org/conda-forge/streamlit_passwordless


.. |LICENSE| image:: https://img.shields.io/pypi/l/streamlit-passwordless?style=plastic
   :alt: PyPI - License
   :target: https://github.com/antonlydell/streamlit-passwordless/blob/main/LICENSE


.. |PyPI| image:: https://img.shields.io/pypi/v/streamlit-passwordless?style=plastic
   :alt: PyPI
   :target: https://pypi.org/project/streamlit-passwordless/


.. |Python| image:: https://img.shields.io/pypi/pyversions/streamlit-passwordless?style=plastic
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/streamlit-passwordless/

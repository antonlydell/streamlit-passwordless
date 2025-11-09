# Streamlit Passwordless

[![PyPI](https://img.shields.io/pypi/v/streamlit-passwordless?color=%23F37726&logo=pypi&logoColor=white)](https://pypi.org/project/streamlit-passwordless/)
[![Conda](https://img.shields.io/conda/vn/conda-forge/streamlit_passwordless?color=%23F37726&logo=anaconda&logoColor=white)](https://anaconda.org/conda-forge/streamlit_passwordless)
[![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/streamlit_passwordless?color=%23F59E42&logo=anaconda&logoColor=white)](https://anaconda.org/conda-forge/streamlit_passwordless)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://pypi.org/project/streamlit-passwordless/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/antonlydell/streamlit-passwordless/blob/main/LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.24+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![View Examples](https://img.shields.io/badge/View-Examples-green.svg)](examples/README.md)

---


## 🔐 Modern Passwordless Authentication for Streamlit Applications

**Streamlit Passwordless** enables secure, passwordless authentication for Streamlit apps using **Passkeys** powered by **Bitwarden Passwordless.dev**.

It provides ready-to-use Streamlit components, a full SQLAlchemy user model, and a command-line interface
— so you can add **Passkey (FIDO2)** sign-in to your Streamlit app in minutes.

👉 **Live demo:** [https://passwordless.streamlit.app](https://passwordless.streamlit.app)

---


# 📚 Table of Contents

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#-configuration)
- [🚀 Example](#-example)
  - [🧩 Quick Start (SQLite)](#-quick-start-sqlite)
  - [💾 Using Another Database Backend](#-using-another-database-backend)
  - [🔒 Role-Based Page Authorization](#-example-role-based-page-authorization)
- [🧩 Examples](#-examples)
- [🧱 Architecture & Import Conventions](#-architecture--import-conventions)
- [💻 CLI Usage](#-cli-usage)
- [🧱 Database Models](#-database-models)
- [🧭 Project Status](#-project-status)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📚 Resources](#-resources)
- [📖 API Reference](#-api-reference)

---


## ✨ Features

- 🔐 Streamlit components for passkey registration, sign-in, and sign-out
- 🧩 Built-in SQLAlchemy models for users, roles, emails, and sign-ins
- 🛡️ Role-based authorization for individual Streamlit pages via the decorator API
- 🧱 Compatibility with any SQL backend (e.g. **SQLite**, **PostgreSQL**, **Microsoft SQL Server**)
- ⚙️ Simple configuration via environment variables or Streamlit secrets
- 💻 CLI tools for database initialization and administration
- 🧑‍💻 Native integration with Streamlit’s UI and state model
- 💡 Fully type-hinted and documented

---


## 📦 Installation

Install from [PyPI](https://pypi.org/project/streamlit-passwordless/):

```bash
pip install streamlit-passwordless
```

Install from [conda-forge](https://anaconda.org/conda-forge/streamlit_passwordless):

```bash
conda install conda-forge::streamlit_passwordless
```

---


## ⚙️ Configuration

**Streamlit Passwordless** can be configured via **environment variables** or the Streamlit secrets' file
(`.streamlit/secrets.toml` or `~/.streamlit/secrets.toml`).

| Variable              | Description                                                                         | Default                               |
|-----------------------|-------------------------------------------------------------------------------------|---------------------------------------|
| `STP_DB_URL`          | SQLAlchemy database URL                                                             | `sqlite:///streamlit_passwordless.db` |
| `STP_BWP_PUBLIC_KEY`  | Bitwarden Passwordless.dev public key                                               | **Required**                          |
| `STP_BWP_PRIVATE_KEY` | Bitwarden Passwordless.dev secret key                                               | **Required**                          |
| `STP_DB_SCHEMA`       | Optional schema name for e.g. PostgreSQL or SQL Server (environment variable only)  | `None`                                |

---


## 🚀 Example

This section shows two ways to get started:

1. **Quick Start (SQLite)** — easiest way to try it out.
2. **Using Another Database Backend** — for production environments.


### 🧩 Quick Start (SQLite)


#### 1. Create a project directory and virtual environment:

   ```bash
   ~ $ mkdir stp_demo && cd stp_demo
   ~/stp_demo $ python -m venv .venv
   ~/stp_demo $ source .venv/bin/activate  # (on Windows: .venv\bin\Activate.ps1)
   ~/stp_demo (.venv) $ python -m pip install streamlit-passwordless
   ~/stp_demo (.venv) $ mkdir .streamlit && touch .streamlit/secrets.toml
   ```


#### 2. Add your [Bitwarden Passwordless.dev](https://admin.passwordless.dev/Account/Login) keys to `.streamlit/secrets.toml`:

   ```toml
   [streamlit-passwordless]
   STP_BWP_PUBLIC_KEY = "<PUBLIC_KEY>"
   STP_BWP_PRIVATE_KEY = "<PRIVATE_KEY>"
   ```


#### 3. Create `app.py`:

   ```python
   # app.py
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
   ```


#### 4. Run the app:

   ```bash
   ~/stp_demo (.venv) $ streamlit run app.py

   You can now view your Streamlit app in your browser.

   Local URL: http://localhost:8501
   ```

   Open your favorite browser at [http://localhost:8501](http://localhost:8501)
   and enjoy passwordless registration and sign-in! 🔑

---


### 💾 Using Another Database Backend

To use another database backend, update `STP_DB_URL` in your secrets file or environment variable:

```toml
[streamlit-passwordless]
STP_DB_URL = "postgresql+psycopg://user:password@localhost/stp_demo"
STP_BWP_PUBLIC_KEY = "<PUBLIC_KEY>"
STP_BWP_PRIVATE_KEY = "<PRIVATE_KEY>"
```

**Example connection URLs:**

| Database   | Example URL                                                                          |
|----------- |--------------------------------------------------------------------------------------|
| PostgreSQL | `postgresql+psycopg://user:password@localhost/dbname`                                |
| SQL Server | `mssql+pyodbc://user:password@localhost/dbname?driver=ODBC+Driver+18+for+SQL+Server` |
| MySQL      | `mysql+pymysql://user:password@localhost/dbname`                                     |

Once configured, initialize the database and create an admin user via the [CLI](#-cli-usage).

---


### 🔒 Role-Based Page Authorization

Restrict access to Streamlit pages based on user roles using the decorator API:

```python
import streamlit as st
import streamlit_passwordless as stp

@stp.authorized(role=stp.AdminRole, redirect="sign_in_page.py")
def admin():
    st.title("Admin Page")
    st.write("Only signed-in admins can view this page.")

if __name__ == '__main__':
    admin()
```

If a non-admin user attempts to access this page, they will automatically be redirected to the sign-in page.

---


## 🧩 Examples

The [examples](examples/README.md) directory includes ready-to-run demonstration apps showing how to use
**Streamlit Passwordless** in different contexts:

| Example | Description                    |
|----------|-------------------------------|
| [`examples/mwp.py`](examples/mwp.py)     | 🧱 A **minimal single-page** Streamlit app demonstrating basic passkey registration and sign-in. This corresponds to the [Quick Start (SQLite)](#-quick-start-sqlite) example in this README. |
| [`examples/app`](examples/app/README.md) | 🔐 A **multi-page Streamlit app** showcasing the core features of Streamlit Passwordless — including registration, sign-in, role-based authorization, and automatic page redirects.           |

👉 Try out and explore the examples above locally to better understand how Streamlit Passwordless works.

> **Note:** Run the examples from inside the `examples/` directory (`cd examples`) to avoid import errors.


### ▶️ Running the Examples

Each example can be launched directly with Streamlit from your local terminal.


#### Run the minimal single-page app:

```bash
cd examples
streamlit run mvp.py
```


#### Run the multi-page app:

```bash
cd examples
streamlit run app/main.py
```

Then open your browser at http://localhost:8501  
You can register new users, sign in, and explore the authentication and authorization flows.

---


## 🧱 Architecture & Import Conventions

**Streamlit Passwordless** is designed with a clear, discoverable import structure.

Always import the package under the alias `stp`:

```python
import streamlit_passwordless as stp
```


### Top-Level Namespace

Common entry points are available directly on `stp` (this is a **short, non-exhaustive** list):

```python
# Setup & session
stp.setup()
stp.authenticated()
stp.get_current_user()

# Built-in UI
stp.bitwarden_register_form()
stp.bitwarden_register_form_existing_user()
stp.bitwarden_sign_in_button()
stp.bitwarden_sign_in_form()
stp.sign_out_button()

# Authorization
stp.authorized()

# Models (commonly imported when interacting with user data)
from streamlit_passwordless import User, Role, CustomRole, Email, UserSignIn

# Default roles
from streamlit_passwordless import Viewer, UserRole, SuperUser, Admin
```

> *Note: Most UI functions require a Bitwarden Passwordless.dev client (client) and a database session (db_session). See the [Examples](#-examples) section for complete usage.*


### Database Access

All database functionality is available under `stp.db`, with SQLAlchemy models exposed via `stp.db.models`.

```python
# Database helpers
stp.db.init()
stp.db.get_user_by_user_id()

# Models
from streamlit_passwordless.db.models import User, Role, CustomRole, Email, UserSignIn
```

This modular layout keeps everyday usage simple (`stp.*`), while making lower-level pieces (`stp.db.*`) easy to find.

> For a detailed API reference, see the [API Reference](#-api-reference) section *(coming soon)*.


## 💻 CLI Usage

**Streamlit Passwordless** includes a convenient command-line interface (CLI) called `stp`.


### Initialize the Database

Create the tables and the default roles (Viewer, User, SuperUser, Admin):

```bash
stp run init
```

This will launch a small Streamlit app that:

- Creates and initializes the database if it does not exist
- Allows you to **create the first admin user**


### Launch the Admin Interface

Once initialized, you can manage users and passkeys via the admin web interface:

```bash
stp run admin
```

This launches the  **Streamlit Passwordless Admin App** where only admin users can:

- Sign in securely using passkeys
- Create, modify, enable, or disable users
- Register additional passkeys for users

Perfect for managing your app’s user base directly from the browser.

> **Note:** the admin app is still experimental and not yet feature-complete.

---


## 🧱 Database Models

The following SQLAlchemy models are included:

| Model        | Description                                                              |
|--------------|--------------------------------------------------------------------------|
| `User`       | Represents an application user                                           |
| `Role`       | Predefined roles: Viewer, User, SuperUser, Admin (extendable if needed)  |
| `CustomRole` | App-specific user roles                                                  |
| `Email`      | User email addresses and verification info                               |
| `UserSignIn` | Tracks sign-in attempts and metadata                                     |


The models include **audit columns** (`updated_at`, `updated_by`, `created_at`, `created_by`)
and work seamlessly with an SQL backend.

---


## 🧭 Project Status

⚠️ **Active development — no stable API yet.**

**Roadmap:**

- [ ] Admin UI enhancements (create and update roles and emails)
- [ ] Support for step-up authentication
- [ ] Support for magic-link sign in and email verification
- [ ] Improved error handling and display of passkey related errors

---


## 🤝 Contributing

The project is open-source but *not open contribution*.  
Feature requests and suggestions are welcome — but **pull requests are not currently accepted.**  
Contributions focused on bug reports and documentation improvements are especially welcome.

---


## 📄 License

**Streamlit Passwordless** is distributed under the [MIT License](https://opensource.org/licenses/mit-license.php).

---


## 📚 Resources

- [Bitwarden Passwordless.dev](https://bitwarden.com/products/passwordless/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLAlchemy Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)

---


## 📖 API Reference

Detailed API documentation for **Streamlit Passwordless** will be available in future releases.

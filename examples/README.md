# 🧩 Streamlit Passwordless Examples

**Secure authentication demos built with [Streamlit Passwordless](https://github.com/antonlydell/streamlit-passwordless)**  
🔐 Passkey registration • 👤 Sign-in • 🛡️ Role-based access • 🚪 Redirects  

[![Streamlit](https://img.shields.io/badge/Streamlit-1.24+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://pypi.org/project/streamlit-passwordless/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/antonlydell/streamlit-passwordless/blob/main/LICENSE)
[![Main Project](https://img.shields.io/badge/View-Main_Project-green.svg)](https://github.com/antonlydell/streamlit-passwordless)

---

This folder includes two example applications.  
A **minimal single-page app** and a **multi-page app** demonstrating the full feature set of **Streamlit Passwordless**.

- `mvp.py` — A minimal Streamlit application demonstrating basic passkey registration and sign-in.  
- `app/` — A Multi-Page Streamlit application showcasing the core features of Streamlit Passwordless,
  including registration, sign-in, authorization, and automatic redirects.

---


## ⚙ Setup

Before running any of the examples, you need to configure your [Bitwarden Passwordless.dev](https://admin.passwordless.dev/Account/Login) credentials.  
These are required for authenticating users with passkeys.

Add your keys to `.streamlit/secrets.toml` or `~/.streamlit/secrets.toml`:

```toml
[streamlit-passwordless]
STP_BWP_PUBLIC_KEY = "<PUBLIC_KEY>"
STP_BWP_PRIVATE_KEY = "<PRIVATE_KEY>"
```

---


## 🧩 Minimal Single-Page App

The single-page example is the quickest way to see **Streamlit Passwordless** in action.

It demonstrates how to:

- 🔑 Register a new user with a passkey (via Bitwarden Passwordless.dev)
- 👤 Sign in securely without a password
- 🚪 Sign out from the session


### ▶️ Run the Example

```bash
streamlit run mvp.py
```

Open your browser at [http://localhost:8501](http://localhost:8501).  
You’ll be able to register and sign in using a passkey in just a few seconds.

---


## 🧱 Multi-Page App

The multi-page demo expands on the minimal example and demonstrates the core features of **Streamlit Passwordless**, including:

- 🔐 Passkey registration and sign-in via Bitwarden Passwordless.dev
- 🛡️ Role-based authorization and page-level access control
- 🔁 Automatic page redirects for unauthorized users and after successful sign-in

---

### 🚀 Setup and Run


#### 1. Initialize the database and create an admin user:

```bash
stp run init
```

This launches a Streamlit app that initializes the database schema and allows you to create the first admin user.


#### 2. Run the example app:

```bash
streamlit run app/main.py
```

> **Note:** Run the examples from inside the `examples/` directory (`cd examples`) to avoid import errors.

Open your browser at [http://localhost:8501](http://localhost:8501).  
You can register new users, sign in, and explore how page access and redirects are managed automatically.

---


### 🧭 About the Demo

The demo includes three pages:

| Icon | Page                     | Access                      |
|------|--------------------------|-----------------------------|
| 🔐   | **Admin**                | Restricted to admin users   |
| 🏠   | **Home**                 | Visible to signed-in users  |
| 👋   | **Register and Sign In** | Public page (default entry) |

Use the sidebar to navigate between pages after you sign in and test the role-based authorization and sign-out flows.

---


### 🧩 Example Overview

This demo uses the built-in features of **Streamlit Passwordless**:

- `@stp.authorized()` — Decorator for page-level authorization
- `stp.authenticated()` — Session user validation
- `stp.bitwarden_register_form()` — Passkey registration
- `stp.bitwarden_register_form_existing_user()` — Passkey registration for signed-in users
- `stp.bitwarden_sign_in()` — Passkey sign-in for registered users
- `stp.sign_out_button()` — Secure sign-out handling
- `st.Page()` and `st.navigation()` — Streamlit’s native multi-page routing

Together, these components show how to build secure, passwordless multi-page Streamlit apps in just a few lines of code.

---


## 💡 Next Steps

Explore the full documentation and [README](../README.md) for more details on configuration, architecture, and CLI usage.  
These examples are a great starting point for integrating **Streamlit Passwordless** into your own Streamlit apps.

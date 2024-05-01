# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]


## [0.2.0] - 2024-04-19

First draft of the register form and interaction with the Bitwarden Passwordless API.


### Added

- `streamlit_passwordless.bitwarden_register_form` : Renders the Bitwarden Passwordless register
  form, which allows the user to register an account with the application by creating and
  registrering a passkey with the user's device.

- `streamlit_passwordless.BitwardenPasswordlessClient` : The client for
  interacting with Bitwarden Passwordless.

  - `register_user` : Register a new user by creating and registring a passkey with the user's device.

- `streamlit_passwordless.BitwardenRegisterConfig` : The available passkey
  configuration when registering a new user.

- `streamlit_passwordless.RegisterUserError` : Raised for errors when registering a new user.

- Icons that can be used for *errors*, *successful operations* and *warnings* within your
  Streamlit application:

  - `streamlit_passwordless.ICON_ERROR`
  - `streamlit_passwordless.ICON_SUCCESS`
  - `streamlit_passwordless.ICON_WARNING`


## [0.1.0] - 2024-01-05

A first release and declaration of the project.


### Added

- The initial structure of the project.

- Registration on [PyPI](https://pypi.org/project/streamlit-passwordless/0.1.0/).


[Unreleased]: https://github.com/antonlydell/streamlit-passwordless/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.2.0
[0.1.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.1.0

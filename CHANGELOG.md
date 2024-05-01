# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

- The user data model and database functionality.

- Session state management of authenticated users.

- The admin console to manage users and credentials.


## [0.3.0] - 2024-05-01

Sign in to your app with the sign in form!

The sign in process is only verified with Bitwarden Passwordless.dev, but the session state
management to identify the user as signed in is not implemented yet.


### Added

- `streamlit_passwordless.bitwarden_sign_in_form` : Render the sign in form to let the user
  sign in to the app.

- `streamlit_passwordless.SignInTokenVerificationError` : Raised for errors when the
  backend is verifying the sign in token.

- New methods for `streamlit_passwordless.BitwardenPasswordlessClient` :

  - `sign_in` : Start the sign in process in the web browser.

  - `verify_sign_in` : Verify the sign in token with the backend to complete the sign in process.

- `streamlit_passwordless.BitwardenPasswordlessVerifiedUser` : A verified user from Bitwarden
  Passwordless. The model is generated after a successful sign in process with
  Bitwarden Passwordless.


### Changed

- Renamed parameter `expires_at` to `validity` of `BitwardenRegisterConfig.` The parameter is now
  a `timedelta` instead of a `datetime` object and defines the number of seconds from the start of
  the registration process that the register token will be valid for. This is necessary because we
  do not know when the user will trigger the registration process from the `bitwarden_register_form`.

- The package now requires Pydantic v2 and is no longer compatible with v1.


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


[Unreleased]: https://github.com/antonlydell/streamlit-passwordless/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.3.0
[0.2.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.2.0
[0.1.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.1.0

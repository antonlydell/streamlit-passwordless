# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

- The user data model and database functionality.

- Session state management of authenticated users.

- The admin console to manage users and credentials.


## [0.5.1] - 2024-05-25

Welcome [Vite](https://vitejs.dev/)!

Changed javascript frontend tooling from the deprecated [react-scripts](https://www.npmjs.com/package/react-scripts)
to [Vite](https://vitejs.dev/). This reduces the number of sub-dependencies and resolves known
security vulnerabilities.


### Security

- Updated javascript dependencies to resolve known vulnerabilities.


## [0.5.0] - 2024-05-24

Buttons with style!

The register and sign in buttons are now styled to look like buttons created with the function
[streamlit.button](https://docs.streamlit.io/develop/api-reference/widgets/st.button). The
styling respects the Streamlit system theme.


### Changed

- `register_button` and `sign_in_button` : Added the parameters `label` and `button_type`, which
  allow to set the label and styling of the buttons. The `button_type` can be either "primary" or
  "secondary" and emulates the `type` parameter of `streamlit.button`.

- `register_form` and `sign_in_form` : Activated the use of the parameters `submit_button_label`
  and `button_type`, which are linked to the `label` and `button_type` parameters of `register_button`
  and `sign_in_button` respectively.


## [0.4.0] - 2024-05-15

Register and sign in from an iPhone!

The issue [#5 iPhone : Client error "The document is not focused"](https://github.com/antonlydell/streamlit-passwordless/issues/5)
is hopefully resolved with the added register and sign in buttons.


### Added

- `streamlit_passwordless.register_button` : Renders the register button, which starts the register
  process when clicked.

- `streamlit_passwordless.sign_in_button` : Renders the sign in button, which starts the sign in
  process when clicked.

- `streamlit_passwordless.BitwardenPasswordlessClient.create_register_token` : Create a register
  token to use for registering a passkey with the user's device.


### Changed

- `streamlit_passwordless.register_form` : The form now uses the new
  `streamlit_passwordless.register_button` and has received parameters to customize the username,
  displayname and alias fields.

- `streamlit_passwordless.sign_in_form` : The form now uses the new
  `streamlit_passwordless.sign_in_button` and has received the parameter `alias_help` to customize
  the help text of the alias field.


### Removed

- `BitwardenPasswordlessClient.register_user` : This method is deprecated and removed since the register
  process is triggered by the new `streamlit_passwordless.register_button`.

- `BitwardenPasswordlessClient.sign_in`  : This method is deprecated and removed since the register
  process is triggered by the new `streamlit_passwordless.sign_in_button`.


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


[Unreleased]: https://github.com/antonlydell/streamlit-passwordless/compare/v0.5.1...HEAD
[0.5.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.5.1
[0.5.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.5.0
[0.4.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.4.0
[0.3.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.3.0
[0.2.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.2.0
[0.1.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.1.0

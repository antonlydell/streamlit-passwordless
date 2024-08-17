# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

- The admin console to manage users and credentials.


## [0.6.1] - 2024-08-17

Fix retrieving http headers from websocket connection for Streamlit >= v1.37.


### Changed

- `streamlit_passwordless.db.create_session_factory` : Changed to only return the session_factory
  and not the engine that is bound to the session_factory. The engine will rarely be of use to the user.

- `streamlit_passwordless.register_from` : Changed the default value from True to False for parameter
  `pre_authorized` since it is a more sensible default value.


### Fixed

- `streamlit_passwordless.register_from` : Properly extracting the http headers from the websocket
  connection using `st.context.headers` for Streamlit >= v1.37. This removes the deprecation warning
  banner.


## [0.6.0] - 2024-08-04

First implementation of the user model!

The user model allows to save registered users to the streamlit-passwordless database.
The database can be an existing or a new database. [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
is used to manage the database interactions and has been added as project dependency.


### Added

- `streamlit_passwordless.db` : All database related objects except for the models.

  - `streamlit_passwordless.db.create_session_factory` : Creates the database session factory,
     which can produce database sessions.

  - `streamlit_passwordless.db.create_user` : Creates a new user.

  - `streamlit_passwordless.db.get_all_users` : Gets all users from the database.

  - `streamlit_passwordless.db.get_user_by_username` : Gets a user by its username.

  - `streamlit_passwordless.db.UserCreate` : The schema for creating a new user.

- `streamlit_passwordless.db.models` : All database models, which describe the tables of the database.

  - `streamlit_passwordless.db.models.User` : The user table.

  - `streamlit_passwordless.db.models.Email` : The email addresses of a user.

- `streamlit_passwordless.BitwardenPasswordlessClient.get_credentials` : Gets the registered passkey
   credentials for a user.


### Changed

- `streamlit_passwordless.register_form` : Added support for saving registered users to the database
   and several other improvements. Some of the highlights are:

  - The *Register* button has been replaced with a *Validate* and a *Register* button to be able
  to validate the form fields before proceeding to register a new passkey credential for the user.
  If the validation does not pass the *Register* button is disabled.

  - The user is now signed in after successful passkey registration.

  - The `pre_authorized` parameter has been implemented, requiring a user to
    exist in the database before allowing registration of passkeys.

  - Added and updated various parameters for improved control of the register form.


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


[Unreleased]: https://github.com/antonlydell/streamlit-passwordless/compare/v0.6.1...HEAD
[0.6.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.6.1
[0.6.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.6.0
[0.5.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.5.1
[0.5.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.5.0
[0.4.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.4.0
[0.3.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.3.0
[0.2.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.2.0
[0.1.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.1.0

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

- The admin console to manage users and credentials.

- Roles and custom roles of the user database model.

- Verifying user email addresses.


## [0.9.0] - 2024-10-12

Improved register form!

`streamlit_passwordless.bitwarden_register_form` may now be configured to let the user set a nickname
for the passkey credential to register and to toggle between a *discoverable* or *non-discoverable*
passkey. A discoverable passkey allows the user to sign in without entering the username in contrast
to a non-discoverable passkey, which is traditionally used for a MFA setup. A discoverable passkey
consumes a passkey slot on a YubiKey, while a non-discoverable does not. In most cases you want to
create a discoverable passkey, which is also the default. The credential nickname field is rendered
by default in the form.


### Added

- `streamlit_passwordless.bitwarden_register_form_existing_user` : Renders the Bitwarden Passwordless register
  form that lets an existing user register additional passkey credentials. It accepts an optional
  `streamlit_passwordless.User` for which to create a passkey credential. If not specified the user from the
  session state key `streamlit_passwordless.SK_USER` is used.


### Changed

- `streamlit_passwordless.bitwarden_register_form` : Added configuration parameters to set a credential nickname
  and to choose between a *discoverable* or *non-discoverable* passkey.


## [0.8.0] - 2024-10-05

Revamped user model!

The user model is now analogous to the database model.

**Breaking Change** : Session state key `SK_BP_VERIFIED_USER` has been renamed to `SK_USER_SIGN_IN` and now
contains a `streamlit_passwordless.UserSignIn` object that replaces
`streamlit_passwordless.BitwardenPasswordlessVerifiedUser`, which has been removed.


### Added

- `streamlit_passwordless.Email` : An Email address of a user.

- `streamlit_passwordless.UserSignIn` : A model of a user sign in with a passkey credential.

- Session state keys:

  - `streamlit_passwordless.SK_DB_USER` : The database object of the current user signed in to the application
    (`streamlit_passwordless.db.models.User`).

  - `streamlit_passwordless.SK_REGISTER_FORM_IS_VALID`: True if the input to the register form is valid and False otherwise.

  - `streamlit_passwordless.SK_USER` : Contains the current user signed in to the application (`streamlit_passwordless.User`).

  - `streamlit_passwordless.SK_USER_SIGN_IN` : Details from Bitwarden Passwordless about the user that signed in
    (`streamlit_passwordless.UserSignIn`).


### Changed

- `streamlit_passwordless.User` : Updated with the fields defined on `streamlit_passwordless.db.models.User`.
  Added a connection to `streamlit_passwordless.Email` and `streamlit_passwordless.UserSignIn` through the
  `emails` and `sign_in` attributes respectively.

- Renamed session state key `SK_BP_VERIFIED_USER` --> `SK_USER_SIGN_IN` : Now contains an instance of
  `streamlit_passwordless.UserSignIn`.

- `streamlit_passwordless.bitwarden_register_form` & `streamlit_passwordless.bitwarden_sign_in_form` :
   Added returning `streamlit_passwordless.User` or `None` from the forms. This will be useful to detect a
   change when a user has registered or signed in when using the `st.fragment` decorator on the forms.


### Fixed

- `streamlit_passwordless.StreamlitPasswordlessError` : Fixed error when accessing the `parent_message` attribute.


### Removed

- `streamlit_passwordless.BitwardenPasswordlessVerifiedUser` : Replaced by `streamlit_passwordless.UserSignIn`,
  which can be accessed from `streamlit_passwordless.User.sign_in`


### Security

- Updated javascript dependencies to resolve security vulnerabilities:
  - *vite* : fixed in version 5.2.14
    - Vite DOM Clobbering gadget found in vite bundled scripts that leads to XSS,
    - Vite's `server.fs.deny` is bypassed when using `?import&raw`.

  - *rollup* : fixed in version 4.22.4
    - DOM Clobbering Gadget found in rollup bundled scripts that leads to XSS.


## [0.7.0] - 2024-09-07

Support to log user sign ins to the database!

When signing in using the sign in form data about the user and passkey credential that signed in
is logged to the database. A user is also signed in after successful passkey registration
using the register form and an entry about the registration sign in is also logged to the database.


### Added

- `streamlit_passwordless.DatabaseError` : Base exception for database related errors.

- `streamlit_passwordless.DatabaseStatementError` : Raised for errors related to the executed SQL statement.

- `streamlit_passwordless.db.commit` : Commit a database transaction within a session.

- `streamlit_passwordless.db.create_user_sign_in` : Create a new user sign in entry in the database.

- `streamlit_passwordless.db.get_user_by_user_id` : Get a user by user_id from the database.

- `streamlit_passwordless.db.UserSignInCreate` : The schema for creating a new user sign in entry.

- `streamlit_passwordless.db.models.UserSignIn` : A logging table of when a user has signed in to the application.


### Changed

- `streamlit_passwordless.register_form` : Added support to save user sign in data to the database.

- `streamlit_passwordless.sign_in_form` : Added support to save user sign in data to the database.

- `streamlit_passwordless.db.create_user` : Added the parameter `commit` to select if the created user
   should be committed to the database after it has been added to the session. The default is to not commit.

- `streamlit_passwordless.db.models.Email` : Added columns `is_primary` and `verified_at`, which describe
  if an email address is the user's primary address and the timestamp when the address was verified by the user.
  Replaced column `active` with `disabled` and `disabled_at` to align the column naming with the user model.

- `streamlit_passwordless.db.models.User` : Added column `verified_at`, which contains the timestamp of
  when a user first verified an email.


## [0.6.1] - 2024-08-17

Fix retrieving http headers from websocket connection for Streamlit >= v1.37.


### Changed

- `streamlit_passwordless.db.create_session_factory` : Changed to only return the session_factory
  and not the engine that is bound to the session_factory. The engine will rarely be of use to the user.

- `streamlit_passwordless.register_form` : Changed the default value from True to False for parameter
  `pre_authorized` since it is a more sensible default value.


### Fixed

- `streamlit_passwordless.register_form` : Properly extracting the http headers from the websocket
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


[Unreleased]: https://github.com/antonlydell/streamlit-passwordless/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.9.0
[0.8.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.8.0
[0.7.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.7.0
[0.6.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.6.1
[0.6.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.6.0
[0.5.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.5.1
[0.5.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.5.0
[0.4.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.4.0
[0.3.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.3.0
[0.2.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.2.0
[0.1.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.1.0

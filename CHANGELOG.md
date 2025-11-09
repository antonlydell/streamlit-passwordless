# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

- Step up authentication.

- Verifying user email addresses.


## [0.18.0] - 2025-11-09

Improved database model and user relationship loading!

The audit columns (`updated_at`, `updated_by`, `created_at` and `created_by`) of the database
models are now deferred from loading by default, since you most often do not want to load these
columns. The string columns of the database models that are or may be subject to indexes are now
length constrained since unbounded string columns cannot be indexed in Microsoft SQL Server.

The `bitwarden_sign_in_form` and `bitwarden_sign_in_button` now support to select which relationships
(custom roles and emails) to load when a user signs in. This will avoid unnecessary database queries
if these objects are not needed in the application.


### Added

- `streamlit_passwordless.authenticated` : A function to check if a user is authenticated.

- `streamlit_passwordless.db.models.audit_columns_mixin_factory` : A function to create the mixin
  class for the audit columns, which allows to customize if the audit columns should be deferred
  from loading in queries by default.

- `streamlit_passwordless.db.models.AUDIT_COLUMNS_GROUP` : The name of the audit columns' group,
  which can be used to undefer all audit columns of a database model in a query.


### Changed

- `streamlit_passwordless.db.models.ModifiedAndCreatedColumnMixin`: Renamed to `AuditColumnsMixin`
  and the audit columns are deferred by default.

- `streamlit_passwordless.db.get_user_by_user_id` : Added the parameters `load_custom_role`, `load_email`,
  `defer_role_description`, `undefer_audit_columns` and `audit_columns_group_name` to control how the
  relationships of the user are loaded.

- `streamlit_passwordless.bitwarden_sign_in_form` and `streamlit_passwordless.bitwarden_sign_in_button` :
  Added the parameters `load_custom_role`, `load_email` and `defer_role_description` to control how the
  relationships of the user are loaded.


## [0.17.0] - 2025-10-11

Proper UUID support for `User.user_id`!

The datatype of the `User.user_id` column in the database has been updated from string to UUID.
Having a proper UUID datatype allows databases (that support UUID) to leverage this datatype
for improved performance and reduced storage space.


### Changed

- `streamlit_passwordless.db.models`:

  - All datetime columns are now generated as timezone aware in database dialects that support
    timezone aware datatypes.

  - `User`, `Email`, `UserSignIn` : Changed datatype of `user_id` column from `str` to `sqlalchemy.Uuid`.

  - `UserSignIn` : Changed dtype of `user_sign_in_id` column from `sqlalchemy.Integer` to `sqlalchemy.BigInteger`
    to better accommodate a large number of user sign in events.

  - `User` : Changed the keying of `custom_roles` dict from `name` to `role_id`.
    It makes more sense to access custom roles by `CustomRole.role_id` rather than `CustomRole.name`,
    since names may change.

- `streamlit_passwordless.User` : Changed the datatype of `user_id` attribute from `str` to `uuid.UUID` and
  the keying of `custom_roles` dict from `name` to `role_id`.


### Removed

- `streamlit_passwordless.db.RoleCreate` : This schema has been replaced with `streamlit_passwordless.Role`.
- `streamlit_passwordless.db.UserCreate` : This schema has been replaced with `streamlit_passwordless.User`.
- `streamlit_passwordless.db.UserSignInCreate` : This schema has been replaced with `streamlit_passwordless.UserSignIn`.


## [0.16.1] - 2025-07-27

Bugfix for connecting to other databases than SQLite!


### Fixed

- `streamlit_passwordless.database.core.enable_sqlite_foreign_keys` : The function can now
  correctly handle connection objects from other database drivers than SQLite without crashing.


## [0.16.0] - 2025-06-27

Typing support and improvements to database creation!

`streamlit_passwordless` now supports the `py.typed` file to play nicely with type checkers.
Creating the database through `streamlit_passwordless.db.create_session_factory` has received
more customization options.


### Added

- `streamlit_passwordless.db`

  - `create_session_factory_cached` : The cached version of  `create_session_factory`.


### Changed

- `streamlit_passwordless.db`

  - `create_session_factory` : Is now a non-cached function. It also supports using a custom
    declarative base class (`sqlalchemy.orm.DeclarativeBase`) when creating the database. This
    is done through the new `base` parameter. The new parameter `connect_args` allows the user
    to pass arguments that will be passed along to the `connect_args` parameter of the
    `sqlalchemy.create_engine` function.


### Fixed

- `streamlit_passwordless.create_user_form` : Fixed allowing to set the desired pre-selected role
  if the default selectable roles are used. Fixed error when `with_custom_roles` was set to False.


## [0.15.0] - 2025-05-17

Updated database model!

Added columns `updated_by`, `created_by` to be able to better track which user has created or
updated a record. Renamed several columns to get better consistency in the naming across
multiple models.


### Added

- `streamlit_passwordless.db.models`

  - `created_at_column` : A table column for the timestamp at which a record was created.

  - `updated_at_column` : A table column for the timestamp at which the record was last modified.

  - `ModifiedAndCreatedColumnMixin` : A table model should inherit from this class prior to
    `streamlit_passwordless.db.models.Base` to add the columns `updated_at`, `modified_by`,
    `created_at` and `created_by`.

  - `CustomRole`, `Email`, `Role`, `User` : Added columns `updated_by`, `created_by`

  - `Email`, `User` : Added column `verified`, which is set to True if an email/user is verified
    and False otherwise.


### Changed

- `streamlit_passwordless` :

  - `bitwarden_register_form`, `bitwarden_register_form_existing_user` : Renamed the default label
    of parameter `credential_nickname_label` from "Credential Nickname" to "Passkey Nickname", which
    is easier to understand for a user. Added parameter `require_credential_nickname`, which is True
    by default and disables the register button if the user has not entered a nickname for the passkey
    credential. It is easy to enter a credential nickname and forget to press Enter to apply the value,
    meaning that a passkey without a nickname will be registered.

  - `bitwarden_register_form`, `create_user_form` : Added parameter `created_by_user_id`, which is the ID
    of the user that is creating the new user.

  - `update_user_form` : Added parameter `updated_by_user_id`, which is the ID of the user that is
    updating the user to update.

- `streamlit_passwordless.db.models` :

  - Removed columns `modified_at` and `created_at` from `Base` database model. If a user of
    `streamlit_passwordless` bases its tables on `Base` he may not want the columns `modified_at`
    and `created_at` added by default to his tables. Moved these columns to the variables
    `updated_at_column` and `created_at_column`, which can be use used in database models as desired.

  - Renamed common table columns `modified_at` --> `updated_at` and `modified_by` --> `updated_by`.

  - `UserSignIn` : Removed column `modified_at`, because records in this table should not be modified
    after creation.

  - `Email`, `User` : Renamed column `disabled_timestamp` -> `disabled_at`,
    which conforms better with the other datetime columns.


## [0.14.1] - 2025-04-26

Bug fix for Python 3.11!


### Fixed

- `streamlit_passwordless` could not be imported using Python 3.11 due to an unsupported f-string
   syntax (`f'{''}'`). This is now resolved.


## [0.14.0] - 2025-04-24

Update and delete users from the Streamlit Passwordless admin app!


### Added

- `streamlit_passwordless.update_user_form` : Update information about an existing user in the database.

- `streamlit_passwordless.delete_user_button` : Delete a user from the database and Bitwarden Passwordless.


### Changed

- `streamlit_passwordless.BitwardenPasswordlessClient.delete_user`: Delete a user from Bitwarden Passwordless.

- `streamlit_passwordless.bitwarden_register_form_existing_user` :  Added support to supply a
  `streamlit_passwordless.db.models.User` in addition to `streamlit_passwordless.User`, which will
  bypass the is authenticated check. This allows the admin user(s) to register passkeys for a selected
  user from the admin page. Added boolean parameter `get_current_user`, which will get the current user
  from the session state if the supplied user is None. If set to False it will ensure that the form is
  disabled if `user` is None.

- `streamlit_passwordless.db` :

  - `get_all_users` : Added typing overloads for better type checking.

  - `get_user_by_user_id` : Updated `disabled` parameter to also accept None, which omits filtering
    by a disabled or enabled user.



## [0.13.0] - 2025-02-27

Create users through the Streamlit Passwordless admin app!

The admin app now contains a form to create users in the database. The form allows
to select the role and custom roles of the user as well as specifying an email address.


### Added

- `streamlit_passwordless.create_user_form` : Create a new user in the database without registering
  a passkey.

- `streamlit_passwordless.get_current_user` : Convenience function to get the current user from the
  session state.

- `streamlit_passwordless.process_form_validation_errors` : Process form validation errors and display
  them in an error banner.

- `streamlit_passwordless.User.email` : A property, which gets the primary email address of the user
  as a string. An empty string is returned if the user does not have any email addresses.

- `streamlit_passwordless.db` :

  - `create_custom_role` : Create a new custom role in the database.

  - `get_all_custom_roles` : Get all custom roles from the database.

  - `get_custom_roles` : Get custom roles by `role_ids` or unique `names`.

  - `get_email` : Get an email from the database.


### Changed

- `streamlit_passwordless.bitwarden_register_form` : Added parameter `banner_container` and
  `redirect` to allow a custom container for error messages and an optional redirect page on
  successful registration. Added support to register an email address for the user through the
  parameters `with_email` and `email_is_username`.

- `streamlit_passwordless.bitwarden_register_form_existing_user` : Added parameters
  `banner_container` and `redirect` to allow a custom container for error messages
  and an optional redirect page on successful registration.

- `streamlit_passwordless.Email.user_id` : Added a default value of an empty string, which makes it
  easier to create a new `streamlit_passwordless.User` with an email address, since the `user_id`
  will be generated when `streamlit_passwordless.User` is initialized and will not be known in
  advance. It is not necessary to specify `streamlit_passwordless.Email.user_id` when saving an
  email to the database since the `user_id` will be derived from its user.

- `streamlit_passwordless.User` :

  - `custom_roles` : Changed the default value of the custom roles to be an empty dict instead of
    None, which is more convenient from a typing perspective to avoid having to check for None.


  - `emails` : Changed the default value to an empty list instead of None, which aligns with the
    default value of `streamlit_passwordless.db.models.User.emails`.

  - `user_id` : Changed the default value from None to an empty string.

- `streamlit_passwordless.db` :

    - `create_user` : Changed the `user` parameter to accept `streamlit_passwordless.User` instead
    of `streamlit_passwordless.db.CreateUser`, since these are basically copies of each other.
    Added support to save the emails of the user to the database.

    - `get_user_by_username` : Changed the `disabled` parameter to accept bool or None. When None
      filtering by disabled or enabled user is omitted.


### Fixed

- `streamlit_passwordless.authorized` : If the decorator was applied more than once in an application the
  user object from the previous execution of the decorator would be used for the authorization of the
  subsequent execution making an authorized user appear not authorized and vice versa. This is now fixed.

- `streamlit_passwordless.db` :

  - `init` : Added rolling back the session if an exception occurs because the default roles already exist
    in the database. This is important otherwise you cannot execute another query using the same session.

  - `models.Email` : Fixed the unique constraint of the `stp_email` table to cover the columns
    (`user_id`, `rank`), not (`email`, `rank`) to ensure a user can have one, and only one,
    primary email address (rank 1).


## [0.12.0] - 2025-01-18

First draft of the Streamlit Passwordless admin app!

The admin app let's you manage the users of your application. The app is launched through the command:
`stp run admin`. This first version only lets admin users sign in to the app and sign out again.
The admin user is created through the init page by running the command `stp run init`.


### Added

- `stp run admin` : The Streamlit Passwordless CLI command to run the admin app.

- `streamlit_passwordless.admin_page` : The main page of the Streamlit Passwordless admin web app.

- `streamlit_passwordless.authorized` : A decorator, which checks if a user is authorized to
  access content of specified role. If the user is authorized the decorated function is executed
  and if not a redirect to another page is possible.

- `streamlit_passwordless.BannerMessageType` : The banner message types defined in Streamlit Passwordless.

- `streamlit_passwordless.bitwarden_sign_in_button` : Allows the user to sign in to the application
  with a discoverable passkey. Similar to `streamlit_passwordless.bitwarden_sign_in_form`, but without the
  possibility to sign in with user_id, alias or a non-discoverable passkey. It also provides the `redirect`
  parameter, which will redirect the user to specified page on successful sign in.

- `streamlit_passwordless.display_banner_message` : Display a message in a banner on a page.

- `streamlit_passwordless.load_config` : Load the configuration for a Streamlit Passwordless application.
  The function result is a cached resource for 6 hours.

- `streamlit_passwordless.sign_out` : Sign out a signed in user. The function is executed when
  `streamlit_passwordless.sign_out_button` is clicked.

- `streamlit_passwordless.sign_out_button` : If clicked the user is signed out from the application.
  The button is disabled if a user is not signed in.

- `streamlit_passwordless.User.is_authorized` : The method checks checks if the user is authorized
  to access content of specified role.

- Added the default roles as instances to facilitate using them in authorization processes. The roles
directly correspond to the roles created in the database when Streamlit Passwordless is initialized:

  - `streamlit_passwordless.ViewerRole` : A user that can only view data within an application.

  - `streamlit_passwordless.UserRole` : The standard user with normal privileges. When a user is
    created it is assigned this role by default.

  - `streamlit_passwordless.SuperUserRole` : A user with higher privileges that can perform certain
    operations that a normal user can not.

  - `streamlit_passwordless.AdminRole` : An admin has full access to everything. Only admin users may
    sign in to the admin page and manage the users of the application. An application should have at
    least one admin.


### Changed

- `streamlit_passwordless.bitwarden_sign_in_form` : The user that signs in can now optionally be
   authorized against a specified role using the new `role` parameter. Added the `banner_container`
   parameter, which allows the user to pass in a custom container in which the error and success
   messages from the sign in form will be written to. The `redirect` parameter can optionally redirect
   the user to specified page on successful sign in. The form now also returns a `success` value,
   which is True if the user was signed in and authorized without errors and False otherwise.

- `streamlit_passwordless.ConfigManager` : Is now immutable.

- `streamlit_passwordless.setup` : Changed the order of the return values from
  (`ConfigManager`, `SessionFactory`, `BitwardenPasswordlessClient`) to
  (`BitwardenPasswordlessClient`, `SessionFactory`, `ConfigManager`).
  This returns the most frequently used objects first. `ConfigManager`
  is not needed in most cases.

- `streamlit_passwordless.UserRoleName`:  Moved to `streamlit_passwordless.db.models.UserRoleName` since
  It makes more sense to keep the `UserRoleName` enum among the database models.


## [0.11.0] - 2025-01-02

Introducing the Streamlit Passwordless CLI (`stp`) and the init page!

The CLI (`stp`) can be used for managing the user database and running the admin web app.
This version of the CLI can launch the initialization page through the command: `stp run init`,
which initializes the database and enables creating an admin account.
The CLI is built with [click](https://click.palletsprojects.com/en/stable/).


### Added

- `stp` : The Streamlit Passwordless CLI.

- Enabling foreign key constraints on connect to a SQLite database.

- `streamlit_passwordless.BITWARDEN_PASSWORDLESS_API_URL` : The default url of the Bitwarden Passwordless backend API.

- `streamlit_passwordless.ConfigManager` : The configuration for running Streamlit Passwordless web apps.

- `streamlit_passwordless.create_bitwarden_passwordless_client` : Create the client to communicate with Bitwarden Passwordless.

- `streamlit_passwordless.DatabaseInvalidUrlError` : Raised for invalid SQLAlchemy database url:s.

- `streamlit_passwordless.init_page` : Initialize the database of Streamlit Passwordless and create an admin account.

- `streamlit_passwordless.setup` : Setup the resources needed to run a Streamlit Passwordless application.

- `streamlit_passwordless.db` :

  - `create_db_url` : Create and validate the database url.

  - `init` : Initialize a database with the required data.
    The default roles of Streamlit Passwordless are created in the database.


### Changed

- `streamlit_passwordless.bitwarden_register_form` : Added returning True or False if a passkey
   was registered or not in addition the user object. This aligns its return value with
   `streamlit_passwordless.bitwarden_register_form_existing_user`.


### Fixed

- `streamlit_passwordless.register_button` and `streamlit_passwordless.sign_in_button` would
   occasionally not execute the registration or sign-in process correctly. This was due to the
   Bitwarden Passwordless custom Streamlit component getting re-initialized when another widget
   on a page got clicked. This resulted in a fresh reload of all JavaScript defined in the component
   and the global state variables would go back to their default values and the buttons would not
   get recognized as clicked although they were clicked. This is now fixed by handling the state
   if the buttons were clicked or not completely on the Python side.

- Bottom border cropping of `streamlit_passwordless.register_button` and `streamlit_passwordless.sign_in_button`.
  The buttons would sometimes get their bottom border cropped by the iframe surrounding the button.
  Added extra bottom margin to the buttons to resolve this issue.


## [0.10.0] - 2024-12-18

Introducing user roles!

A user can be now be associated with a role to manage its privileges within an application.
The available roles are predefined by streamlit-passwordless, but can be extended if needed.
A new user is by default given the "User" role. A User may also have none or many
custom roles, which are defined for each application and may grant application specific
privileges or hide/expose specific pages.


### Added

- `STP_DB_SCHEMA` : The environment variable to specify to set the schema to use for the database.
  If not specified no schema is used.

- `streamlit_passwordless.UserRoleName` : The predefined user role names of streamlit-passwordless.

  - `VIEWER`
      - A user that can only view data within an application.

  - `USER`
      - The standard user with normal privileges. When a user is created it is
        assigned this role by default.

  - `SUPERUSER`
      - A user with higher privileges that can perform certain
        operations that a normal `USER` can not.

  - `ADMIN`
      - An admin has full access to everything. Only admin users may sign in to the admin page
        and manage the users of the application. An application should have at least one admin.

- `streamlit_passwordless.Role` : The role of a user.

- `streamlit_passwordless.CustomRole` : A custom role for a user.

- `streamlit_passwordless.db` :

  - `create_default_roles` : Create the default roles in the database.

  - `create_role` : Create a new role in the database.

  - `get_all_roles` : Get all roles from the database.

  - `get_role_by_name` : Get a role by its unique name.

  - `get_role_by_role_id` : Get a role by role_id

  - `RoleCreate` : The schema for creating a new role.

- `streamlit_passwordless.db.models` :

  - `Role` : The role of a user.

  - `CustomRole` : The custom roles of a user.

- `streamlit_passwordless.SK_ROLES` :
    The session state key for the available roles for a user.

- `streamlit_passwordless.SK_CUSTOM_ROLES` :
    The session state key for the available custom roles for a user.


### Changed

- `streamlit_passwordless.Email` : Renamed parameter `is_primary` to `rank`. `rank` is an integer, where
   1 defines the primary email and 2 the secondary etc ...

- `streamlit_passwordless.db.models` : Improved `__repr__` methods of all database models.

- `streamlit_passwordless.bitwarden_register_form` : Added the parameter `role`, which allows
  to set the role of a user when a new user is created. It defaults to `UserRoleName.USER`.


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

- `streamlit_passwordless.bitwarden_register_form` : Added support to save user sign in data to the database.

- `streamlit_passwordless.bitwarden_sign_in_form` : Added support to save user sign in data to the database.

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

- `streamlit_passwordless.bitwarden_register_form` : Changed the default value from True to False for parameter
  `pre_authorized` since it is a more sensible default value.


### Fixed

- `streamlit_passwordless.bitwarden_register_form` : Properly extracting the http headers from the websocket
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

- `streamlit_passwordless.bitwarden_register_form` : Added support for saving registered users to the database
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

- `bitwarden_register_form` and `bitwarden_sign_in_form` : Activated the use of the parameters `submit_button_label`
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

- `streamlit_passwordless.bitwarden_register_form` : The form now uses the new
  `streamlit_passwordless.register_button` and has received parameters to customize the username,
  displayname and alias fields.

- `streamlit_passwordless.bitwarden_sign_in_form` : The form now uses the new
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


[Unreleased]: https://github.com/antonlydell/streamlit-passwordless/compare/v0.18.0...HEAD
[0.18.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.18.0
[0.17.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.17.0
[0.16.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.16.1
[0.16.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.16.0
[0.15.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.15.0
[0.14.1]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.14.1
[0.14.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.14.0
[0.13.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.13.0
[0.12.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.12.0
[0.11.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.11.0
[0.10.0]: https://github.com/antonlydell/streamlit-passwordless/releases/tag/v0.10.0
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

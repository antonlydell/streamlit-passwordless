r"""Components related to the frontend library of Bitwarden Passwordless."""

# Standard library
from pathlib import Path

# Third party
import streamlit.components.v1 as components

_RELEASE = True
_COMPONENT_NAME = 'bitwarden_passwordless'
_BUILD_DIR = Path(__file__).parent / 'frontend' / 'build'
_DEV_URL = 'http://localhost:3001'


if _RELEASE:
    _bitwarden_passwordless_func = components.declare_component(_COMPONENT_NAME, path=_BUILD_DIR)  # type: ignore
else:
    _bitwarden_passwordless_func = components.declare_component(name=_COMPONENT_NAME, url=_DEV_URL)


def register_button(
    register_token: str,
    public_key: str,
    credential_nickname: str,
    disabled: bool = False,
    key: str | None = None,
) -> tuple[str, dict | None]:
    r"""Render the register button, which starts the register process when clicked.

    The register process creates and registers a passkey with the user's device.

    The return value from the button is also saved to the session state with a key
    defined by the `key` parameter if `key` is not None.

    Parameters
    ----------
    register_token : str
        The registration token used to authorize the creation of a passkey on the user's device.

    public_key : str
        The public key of the Bitwarden Passwordless application.

    credential_nickname : str
        A nickname for the passkey credential being registered to use for easier identification
        of the device being registered.

    disabled : bool, default False
        If True the button will be disabled and if False the button will be clickable.

    key : str or None, default None
        An optional key that uniquely identifies this component. If this is None, and the
        component's arguments are changed, the component will be re-mounted in the Streamlit
        frontend and lose its current state.

    Returns
    -------
    token : str
        The public key of the created passkey, which the user will use for future sign-in
        operations. This key is saved to the Bitwarden Passwordless database. An empty string
        is returned if the button has not been clicked.

    error : dict
        An error object containing information about if the registration process was successful
        or not. None is returned if no errors occurred during the register process or if the
        button has not been clicked.
    """

    value = _bitwarden_passwordless_func(
        action='register',
        register_token=register_token,
        public_key=public_key,
        credential_nickname=credential_nickname,
        disabled=disabled,
        key=key,
    )

    if value is None:
        return '', None
    else:
        token, error = value
        return token, error


def sign_in_button(
    public_key: str,
    alias: str | None = None,
    with_discoverable: bool = True,
    with_autofill: bool = False,
    disabled: bool = False,
    key: str | None = None,
) -> tuple[str, dict | None]:
    r"""Render the sign in button, which starts the sign in process when clicked.

    Uses the Bitwarden Passwordless javascript frontend client.

    The return value from the button is also saved to the session state with a key
    defined by the `key` parameter if key is not None.

    Parameters
    ----------
    public_key : str
        The public key of the Bitwarden Passwordless application.

    alias : str or None, default None
        The alias of the user to sign in. If specified it will override the other sign in
        methods `with_discoverable`, and `with_autofill`.

    with_discoverable : bool, default True
        If True the browser's native UI prompt will be used to select the passkey to use for
        signing in. If False the sign in method is disabled. If True it will override the
        value of the `with_autofill` parameter. If `alias` is specified it will override this
        sign in method.

    with_autofill : bool, default False
        If True the browser's native autofill UI will be used to select the passkey to use for
        signing in. If False the sign in method is disabled. This method of signing in is
        overridden if `alias` is specified or `with_discoverable` is True.

    disabled : bool, default False
        If True the button will be disabled and if False the button will be clickable.

    key : str or None, default None
        An optional key that uniquely identifies this component. If this is None, and the
        component's arguments are changed, the component will be re-mounted in the Streamlit
        frontend and lose its current state.

    Returns
    -------
    token : str
        The verification token to be used by the Bitwarden Passwordless backend to authenticate
        the sign in process. An empty string is returned if the button has not been clicked.

    error : dict | None
        An error object containing information if there was an error with the sign in process.
        None is returned if no errors occurred during the sign in process or if the button
        has not been clicked.
    """

    value = _bitwarden_passwordless_func(
        action='sign_in',
        public_key=public_key,
        alias=alias,
        with_discoverable=with_discoverable,
        with_autofill=with_autofill,
        disabled=disabled,
        key=key,
    )

    if value is None:
        return '', None
    else:
        token, error = value
        return token, error

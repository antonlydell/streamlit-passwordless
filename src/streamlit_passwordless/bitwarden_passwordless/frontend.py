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
    _bitwarden_passwordless_func = components.declare_component(_COMPONENT_NAME, path=_BUILD_DIR)
else:
    _bitwarden_passwordless_func = components.declare_component(name=_COMPONENT_NAME, url=_DEV_URL)


def register(register_token: str, key=None) -> tuple[str, dict]:
    r"""Register a new user by creating and registring a passkey with the user's device.

    Parameters
    ----------
    register_token : str
        The registration token used to authorize the creation of a passkey on the user's device.

    key : str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    token : str
        The public key of the created passkey, which the user will use for future sign-in
        operations. This key is saved to the Bitwarden Passwordless database.

    error : dict
        An error object containing information about if the registration process was
        successful or not.
    """

    value = _bitwarden_passwordless_func(action='register', token=register_token, key=key)

    if value is None:
        return ('', {})
    else:
        return value

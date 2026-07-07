"""Components related to the frontend library of Bitwarden Passwordless."""

# Standard library
from importlib.resources import files
from typing import Literal, TypeAlias, TypedDict, cast

# Third party
import streamlit as st

from streamlit_passwordless.exceptions import StreamlitPasswordlessError

_BUILD_DIR = files('streamlit_passwordless.bitwarden_passwordless').joinpath('frontend/build')

BUTTON_TYPE: TypeAlias = Literal['primary', 'secondary', 'tertiary']


class FrontendError(TypedDict):
    type: str
    title: str
    status: int
    errorCode: str | None
    traceId: str | None
    source: str


class TriggerResult(TypedDict):
    """The result from a Bitwarden Passwordless authentication workflow.

    Parameters
    ----------
    action : str
        The action performed by the Bitwarden Passwordless function.

    ok : bool
        True if the action was successful and False otherwise.

    token : str
        The token produced by the frontend after successful authentication,
        which should be verified by the backend.

    error : FrontendError or None
        An object with error information if the workflow was unsuccessful.
        None is returned if the executed action was successful.
    """

    action: str
    ok: bool
    token: str | None
    error: FrontendError | None


class FrontendResult(TypedDict):
    """The result always returned from a Bitwarden Passwordless frontend function.

    Parameters
    ----------
    busy : bool
        True if an authentication workflow is in progress and false otherwise.

    result : TriggerResult or None
        The result from a Bitwarden Passwordless authentication workflow.
        None is returned if an authentication workflow has not been triggered
        by clicking the frontend button.
    """

    busy: bool
    result: TriggerResult | None


def _load_assets(name: str) -> str:
    """Load the CSS and JavaScript assets of the custom component.

    Parameters
    ----------
    name : str
        The name of asset file to load.

    Returns
    -------
    content : str
        The content of the loaded asset.

    Raises
    ------
    streamlit_passwordless.StreamlitPasswordlessError
        If the asset file is empty or if it is not a file.
    """

    path = _BUILD_DIR.joinpath(name)

    if not path.is_file():
        raise StreamlitPasswordlessError(
            f'The asset file "{path}" does not exist or is a directory!'
        )

    content = path.read_text(encoding='UTF-8')
    if not content:
        raise StreamlitPasswordlessError(f'The asset file "{path}" is empty!')

    return content


_CSS = _load_assets(name='button.css')
_JS = _load_assets(name='index.js')

_bwp_func = st.components.v2.component(
    name='bitwarden_passwordless',
    html='<button class="bwp-button"></button>',
    js=_JS,
    css=_CSS,
    isolate_styles=False,
)


def register_button(
    register_token: str,
    public_key: str,
    credential_nickname: str,
    disabled: bool = False,
    label: str = 'Register',
    button_type: BUTTON_TYPE = 'primary',
    key: str | None = None,
) -> FrontendResult:
    """Render the register button, which starts the register process when clicked.

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

    label : str, default 'Register'
        The label of the button.

    button_type : Literal['primary', 'secondary', 'tertiary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    key : str or None, default None
        An optional key that uniquely identifies this component. If this is None, and the
        component's arguments are changed, the component will be re-mounted in the Streamlit
        frontend and lose its current state.

    Returns
    -------
    streamlit_passwordless.FrontendResult
        The result of running the register process.
    """

    data = {
        'action': 'register',
        'register_token': register_token,
        'public_key': public_key,
        'credential_nickname': credential_nickname,
        'disabled': disabled,
        'label': label,
        'button_type': button_type,
    }

    return cast(FrontendResult, _bwp_func(data=data, key=key))


def sign_in_button(
    public_key: str,
    alias: str | None = None,
    with_discoverable: bool = True,
    with_autofill: bool = False,
    disabled: bool = False,
    label: str = 'Sign in',
    button_type: BUTTON_TYPE = 'primary',
    key: str | None = None,
) -> FrontendResult:
    """Render the sign in button, which starts the sign in process when clicked.

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

    label : str, default 'Register'
        The label of the button.

    button_type : Literal['primary', 'secondary', 'tertiary'], default 'primary'
        The styling of the button. Emulates the `type` parameter of :func:`streamlit.button`.

    key : str or None, default None
        An optional key that uniquely identifies this component. If this is None, and the
        component's arguments are changed, the component will be re-mounted in the Streamlit
        frontend and lose its current state.

    Returns
    -------
    streamlit_passwordless.FrontendResult
        The result of running the sign in process.
    """

    data = {
        'action': 'sign_in',
        'public_key': public_key,
        'alias': alias,
        'with_discoverable': with_discoverable,
        'with_autofill': with_autofill,
        'disabled': disabled,
        'label': label,
        'button_type': button_type,
    }

    return cast(FrontendResult, _bwp_func(data=data, key=key))

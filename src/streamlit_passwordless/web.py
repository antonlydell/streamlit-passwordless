r"""Functions to work with the browser and the underlying websocket connection of Streamlit."""

# Standard library
import logging

# Third party
import streamlit as st

if (context := getattr(st, 'context', None)) is None:
    from streamlit.web.server.websocket_headers import _get_websocket_headers
else:  # streamlit >= 1.37

    def _get_websocket_headers() -> dict[str, str] | None:
        return getattr(context, 'headers', None)


# Local
from streamlit_passwordless import exceptions

logger = logging.getLogger(__name__)


def get_websocket_headers() -> dict[str, str]:
    r"""Get the HTTP request headers passed along to the websocket connection.

    Returns
    -------
    headers : dict[str, str]
        A copy of the HTTP request headers.

    Raises
    ------
    streamlit_passwordless.StreamlitPasswordlessError
        If no headers could be retrieved from the websocket connection.
    """

    headers = _get_websocket_headers()

    if headers is None:
        error_msg = 'No HTTP request headers received from websocket connection!'
        logger.error(error_msg)
        raise exceptions.StreamlitPasswordlessError(error_msg)

    return headers


def get_origin_header() -> str:
    r"""Get the Origin HTTP request header of to the websocket connection.

    Returns
    -------
    origin : str
        The Origin http request header.

    Raises
    ------
    streamlit_passwordless.StreamlitPasswordlessError
        If no headers could be retrieved from the websocket connection or if
        the "Origin" header was not found.
    """

    headers = get_websocket_headers()
    origin = headers.get('Origin')

    if origin is None:
        error_msg = 'Origin http header not found in websocket connection!'
        logger.error(error_msg)
        raise exceptions.StreamlitPasswordlessError(error_msg)

    return origin

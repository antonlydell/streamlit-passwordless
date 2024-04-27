r"""The exception hierarchy of streamlit-passwordless."""

# Standard library
from typing import Any


class StreamlitPasswordlessError(Exception):
    r"""The base Exception of streamlit-passwordless.

    Parameters
    ----------
    message : str
        The exception message.

    data : Any, default None
        Optional extra data to include in the exception.
    """

    def __init__(self, message: str, data: Any = None) -> None:
        self.data = data
        super().__init__(message)


class RegisterUserError(StreamlitPasswordlessError):
    r"""Raised for errors when registering a new user."""


class SignInTokenVerificationError(StreamlitPasswordlessError):
    r"""Raised for errors when the backend is verifying the sign in token."""

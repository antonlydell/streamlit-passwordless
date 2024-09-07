r"""The exception hierarchy of streamlit-passwordless."""

# Standard library
from typing import Any


class StreamlitPasswordlessError(Exception):
    r"""The base Exception of streamlit-passwordless.

    Parameters
    ----------
    message : str
        The error message.

    data : Any, default None
        Optional extra data to include in the exception.

    e : Exception or None, default None
        The parent exception that is being wrapped and is
        used to extract additional error information from.

    Attributes
    ----------
    message : str
        The error message of the `message` parameter.

    name : str
        The name of the exception.

    parent_exception : Exception or None
        The wrapped parent exception if provided.

    parent_exception_name : str or None
        The name with module path of `parent_exception`.

    parent_message : str or None
        The error message of the parent exception.

    parent_full_message : str or None
        The full error message of the parent exception.
    """

    def __init__(self, message: str, data: Any = None, e: Exception | None = None) -> None:
        self.message = message
        self.data = data
        self.name = self.__class__.__name__

        if e is not None:
            self.parent_exception: Exception | None = e
            self.parent_exception_name: str | None = f'{e.__module__}.{e.__class__.__name__}'
            self.parent_full_message: str | None = str(e)
        else:
            self.parent_exception = None
            self.parent_exception_name = None
            self.parent_full_message = None

        if not getattr(self, 'parent_message'):
            self.parent_message = None if e is None else self._get_parent_error_message(e=e)

        super().__init__(message)

    @staticmethod
    def _get_parent_error_message(e: Exception) -> Any:
        r"""Get the error message of the parent exception."""

        try:
            return e.args[0]
        except KeyError:
            return None

    @property
    def displayable_message(self) -> str:
        r"""An error message that is safe to display to the user."""

        return self.message

    @property
    def detailed_message(self) -> str:
        r"""An error message with more details.

        It may contain more sensitive data that should not be displayed to the user.
        It is useful to log this message.
        """

        return (
            f'{self.message}\nParent Exception : {self.parent_exception_name}\n'
            f'{self.parent_full_message}'
        )


class RegisterUserError(StreamlitPasswordlessError):
    r"""Raised for errors when registering a new user."""


class SignInTokenVerificationError(StreamlitPasswordlessError):
    r"""Raised for errors when the backend is verifying the sign in token."""


class DatabaseError(StreamlitPasswordlessError):
    r"""Base exception for database related errors.

    Attributes
    ----------
    db_api_exception_name : str or None
        The name with module path to the underlying database api exception
        that triggered the database error.
    """

    def __init__(self, message: str, e: Exception | None = None) -> None:
        if e is not None:
            self.db_api_exception_name = self._get_db_api_exception_name(e=e)
            self.parent_message = self._get_parent_error_message(e=e)
        else:
            self.db_api_exception_name = None

        super().__init__(message, e=e)

    @staticmethod
    def _get_db_api_exception_name(e: Exception) -> str | None:
        r"""Get the name of the exception raised from the underlying database api."""

        if (orig := getattr(e, 'orig', None)) is None:
            return None
        else:
            return f'{orig.__module__}.{orig.__class__.__name__}'

    @staticmethod
    def _get_parent_error_message(e: Exception) -> str | None:
        r"""Get the error message from the parent exception."""

        if (orig := getattr(e, 'orig', None)) is None:
            return orig
        else:
            return str(orig)

    @property
    def detailed_message(self) -> str:
        return (
            f'{self.name}({self.message})\n'
            f'Parent Exception : {self.parent_exception_name}\n'
            f'DB API Exception : {self.db_api_exception_name}\n'
            f'Parent Exception Message : {self.parent_message}'
        )


class DatabaseStatementError(DatabaseError):
    r"""Raised for errors related to the executed SQL statement.

    Attributes
    ----------
    statement : str or None
        The SQL statement that caused the error.

    params : str or None
        The parameters supplied to `statement`.
    """

    def __init__(self, message: str, e: Exception | None) -> None:
        if e is not None:
            self.statement = getattr(e, 'statement')
            self.params = getattr(e, 'params')
        else:
            self.statement = None
            self.params = None

        super().__init__(message, e=e)

    @property
    def detailed_message(self) -> str:
        return (
            f'{self.name}({self.message})\n'
            f'Parent Exception : {self.parent_exception_name}\n'
            f'DB API Exception : {self.db_api_exception_name}\n'
            f'Statement : {self.statement}\n'
            f'Params : {self.params}\n'
            f'Parent Exception Message : {self.parent_message}'
        )

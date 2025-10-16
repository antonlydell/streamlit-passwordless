r"""Helper functions for testing the database sub-package."""

# Standard library
import contextlib
from collections.abc import Iterator

# Third party
from sqlalchemy import Engine, event


@contextlib.contextmanager
def count_queries(engine: Engine) -> Iterator[list[str]]:
    """Collect the SQL queries executed within a session.

    Parameters
    ----------
    engine : sqlalchemy.Engine
        The database engine in which to listen for SQL statements.

    Yields
    ------
    statements : Iterator[list[str]]
        The executed statements.
    """

    statements: list[str] = []

    def before_cursor_execute(_conn, _cursor, statement, _params, _context, _executemany):
        statements.append(statement)

    event.listen(engine, 'before_cursor_execute', before_cursor_execute)

    try:
        yield statements
    finally:
        event.remove(engine, 'before_cursor_execute', before_cursor_execute)

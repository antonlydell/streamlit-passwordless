r"""The core database functionality."""

# Standard library
import logging
import sqlite3
from typing import TypeAlias

# Third party
from sqlalchemy import URL as _URL
from sqlalchemy import Engine as _Engine
from sqlalchemy import create_engine, event, make_url
from sqlalchemy.exc import SQLAlchemyError, StatementError
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import sessionmaker

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.models import Base

Engine: TypeAlias = _Engine
Session: TypeAlias = _Session
SessionFactory: TypeAlias = sessionmaker[_Session]
URL: TypeAlias = str | _URL

logger = logging.getLogger(__name__)


@event.listens_for(_Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    r"""Enable foreign key constraints in SQLite when a new connection is established."""

    if dbapi_connection.__module__ != 'sqlite3':
        return

    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    except sqlite3.Error as e:
        error_msg = (
            'Error enabling foreign keys for SQLite!\n'
            'Is your version of SQLite < v3.6.19 or compiled with the SQLITE_OMIT_FOREIGN_KEY '
            'or SQLITE_OMIT_TRIGGER symbols enabled?\n'
            f'{e.__module__}.{e.__class__.__name__}({e.args[0]})'
        )
        logger.error(error_msg)

    cursor.close()


def create_session_factory(
    url: URL,
    autoflush: bool = False,
    expire_on_commit: bool = False,
    create_database: bool = True,
    **engine_config,
) -> tuple[SessionFactory, Engine]:
    r"""Create the database session factory, which can produce database sessions.

    The database engine is bound to each session produced by the factory.

    Parameters
    ----------
    url : str or sqlalchemy.URL
        The SQLAlchemy database url.

    autoflush : bool, default False
        Automatically flush pending changes within the session to the database
        before executing new SQL statements.

    expire_on_commit : bool, default False
        If True make the connection between the models and the database expire after a
        transaction within a session has been committed and if False make the database models
        accessible after the commit.

    create_database : bool, default True
        If True the database table schema will be created if it does not exist.

    **engine_config : dict
        Additional keyword arguments passed to the :func:`sqlalchemy.create_engine` function.

    Returns
    -------
    session_factory : streamlit_passwordless.db.SessionFactory
        The session factory that can produce new database sessions.

    engine : streamlit_passwordless.db.Engine
        The database engine that manages the database connections and is bound
        to `session_factory`.
    """

    engine = create_engine(url=url, **engine_config)
    session_factory = sessionmaker(
        bind=engine, autoflush=autoflush, expire_on_commit=expire_on_commit
    )

    if create_database:
        Base.metadata.create_all(bind=engine)

    return session_factory, engine


def commit(session: Session, error_msg: str = 'Error committing transaction!') -> None:
    r"""Commit a database transaction.

    session : streamlit_passwordless.db.Session
        An active database session.

    error_msg : str, default 'Error committing transaction!'
        An error message to add to the raised exception if an error occurs.

    Returns
    -------
    None

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while processing the database transaction.

    streamlit_passwordless.DatabaseStatementError
        If there is an error with the executed SQL statement(s).
    """

    try:
        session.commit()
    except StatementError as e:
        raise exceptions.DatabaseStatementError(message=error_msg, e=e) from None
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError(message=error_msg, e=e) from None


def create_db_url(url: str | URL) -> URL:
    r"""Create and validate the database url.

    Parameters
    ----------
    url : str or sqlalchemy.URL
        The SQLAlchemy database url. If `url` is of type
        :class:`sqlalchemy.URL` it will be returned as is.

    Returns
    -------
    sqlalchemy.URL
        The converted SQLAlchemy database url.

    Raises
    ------
    streamlit_passwordless.DatabaseInvalidUrlError
        If `url` is invalid.
    """

    try:
        return make_url(url)
    except SQLAlchemyError as e:
        raise exceptions.DatabaseInvalidUrlError(message=str(e), url=url, e=e)  # type: ignore

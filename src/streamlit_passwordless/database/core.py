r"""The core database functionality."""

# Standard library
from typing import TypeAlias

# Third party
from sqlalchemy import URL as _URL
from sqlalchemy import Engine as _Engine
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError, StatementError
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import sessionmaker

# Local
from streamlit_passwordless import exceptions

from .models import Base

Engine: TypeAlias = _Engine
Session: TypeAlias = _Session
SessionFactory: TypeAlias = sessionmaker[_Session]
URL: TypeAlias = str | _URL


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

r"""Database operations on the email table stp_email."""

# Standard library

# Third party
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

# Local
from streamlit_passwordless import exceptions
from streamlit_passwordless.database.core import Session
from streamlit_passwordless.database.models import Email


def get_email(session: Session, email: str, load_user: bool = False) -> Email | None:
    r"""Get an email from the database.

    Parameters
    ----------
    session : Session
        An active database session.

    email : str
        The email address to retrieve from the database.

    load_user : bool, default False
        If True the user that that the email belongs to will also be loaded from the database.

    Returns
    -------
    streamlit_passwordless.db.models.Email or None
        The email address matching `email` or None if an email was not found.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while loading the email address from the database.
    """

    query = select(Email).where(Email.email == email)
    if load_user:
        query = query.options(selectinload(Email.user))

    try:
        return session.scalars(query).one_or_none()
    except SQLAlchemyError as e:
        raise exceptions.DatabaseError(
            f'Error loading email "{email}" from database!', e=e
        ) from None

r"""Database operations on the user_sign_in table."""

# Local
from streamlit_passwordless.database import models
from streamlit_passwordless.database.core import Session
from streamlit_passwordless.database.core import commit as db_commit
from streamlit_passwordless.models import UserSignIn


def create_user_sign_in(
    session: Session, user_sign_in: UserSignIn, commit: bool = True
) -> models.UserSignIn:
    r"""Create a new user sign in entry in the database.

    Parameters
    ----------
    session : streamlit_passwordless.db.Session
        An active database session.

    user_sign_in : streamlit_passwordless.UserSignIn
        The user sign in entry to create.

    commit : bool, default True
        True if the added user sign in entry should be committed after being added to the
        session and False to commit later. Note that the returned `db_user_sign_in` object
        will be in a expired state if committing and will be re-loaded from the database upon
        next access.

    Returns
    -------
    db_user_sign_in : streamlit_passwordless.db.models.UserSignIn
        The created user sign in entry.

    Raises
    ------
    streamlit_passwordless.DatabaseError
        If an error occurs while saving the user sign in entry to the database.

    streamlit_passwordless.DatabaseStatementError
        If there is an error with the executed SQL statement.
    """

    db_user_sign_in = models.UserSignIn(**user_sign_in.model_dump())
    session.add(db_user_sign_in)

    if commit:
        error_msg = 'Unable to save user sign in to database! Check the logs for more details.'
        db_commit(session=session, error_msg=error_msg)

    return db_user_sign_in

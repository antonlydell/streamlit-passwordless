r"""The schemas for the UserSignIn model."""

# Standard library
from datetime import datetime

# Third party
from pydantic import AnyHttpUrl, field_validator

# Local
from .core import SchemaBaseModel


class UserSignInCreate(SchemaBaseModel):
    r"""The schema for creating a new user sign in entry.

    Parameters
    ----------
    user_id : str
        The unique ID of the user that signed in to the application.

    sign_in_timestamp : datetime
        The timestamp in timezone UTC when the user signed in.

    success : bool
        True if the user was successfully signed in and False otherwise.

    origin : str
        The domain name or IP-address of the application the user signed in to.

    device : str
        The device the user signed in from. E.g. a web browser.

    country : str
        The country code of the country that the user signed in from. E.g. SE for Sweden.

    credential_nickname : str
        The nickname of the passkey that was used to sign in.

    credential_id : str
        The ID of the passkey credential used to sign in.

    sign_in_type : str
        The type of sign in method. E.g. 'passkey_signin'.

    rp_id : str or None
        The ID of the relaying party, which is the server that
        verifies the credentials during the sign in process.
    """

    user_id: str
    sign_in_timestamp: datetime
    success: bool
    origin: str | AnyHttpUrl
    device: str
    country: str
    credential_nickname: str
    credential_id: str
    sign_in_type: str
    rp_id: str | None

    @field_validator('origin')
    def convert_origin_to_string(cls, v: str | AnyHttpUrl) -> str:
        return v if isinstance(v, str) else str(v)

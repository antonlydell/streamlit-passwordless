r"""The functions and models for interacting with the Bitwarden Passwordless backend API."""

# Standard library
import logging
from datetime import datetime
from typing import Self

# Third party
from passwordless import VerifiedUser
from pydantic import AnyHttpUrl

# Local
from streamlit_passwordless import models

logger = logging.getLogger(__name__)


class BitwardenPasswordlessVerifiedUser(models.BaseModel):
    r"""A verified user from Bitwarden Passwordless.

    The model is generated after a successful sign in process with Bitwarden Passwordless.

    Parameters
    ----------
    success : bool
        True if the user was successfully signed in and False otherwise.

    user_id: str
        The unique ID of the user that signed in.

    sign_in_timestamp : datetime
        The timestamp in timezone UTC when the user signed in.

    origin : AnyHttpUrl
        The domain name or IP-address of the application the user signed in to.

    device : str
        The device the user signed in from. E.g. a web browser.

    country : str
        The country code of the country that the user signed in from, e.g. SE for Sweden.

    credential_nickname : str
        The nickname for the passkey that was used to sign in.

    credential_id : str
        The ID of the passkey credential used to sign in. Base64 encoded.

    expires_at : str
        ?

    token_id : str
        ?

    type : str
        The type of sign in method e.g. 'passkey_signin'.

    rp_id : str or None
        The ID of the relaying party, which is that is the server that
        verifies the credentials during the sign in process.
    """

    success: bool
    user_id: str
    sign_in_timestamp: datetime
    origin: AnyHttpUrl
    device: str
    country: str
    credential_nickname: str
    credential_id: str
    expires_at: datetime
    token_id: str
    type: str
    rp_id: str | None

    def __str__(self) -> str:
        return (
            f'{self.__class__.__name__}(success={self.success}, '
            f'user_id={self.user_id}, '
            f'sign_in_timestamp={self.sign_in_timestamp.strftime(r"%Y-%m-%d %H:%M:%S %z")})'
        )

    @classmethod
    def _from_passwordless_verified_user(cls, verified_user: VerifiedUser) -> Self:
        r"""Create an instance from a `passwordless.VerifiedUser`."""

        return cls(
            success=verified_user.success,
            user_id=verified_user.user_id,
            sign_in_timestamp=verified_user.timestamp,
            origin=verified_user.origin,
            device=verified_user.device,
            country=verified_user.country,
            credential_nickname=verified_user.nickname,
            credential_id=verified_user.credential_id,
            expires_at=verified_user.expires_at,
            token_id=verified_user.token_id,
            type=verified_user.type,
            rp_id=verified_user.rp_id,
        )

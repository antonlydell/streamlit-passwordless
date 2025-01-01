r"""The configuration of Streamlit Passwordless."""

# Standard library
import logging
import os
from typing import Self

# Third party
import streamlit as st
from pydantic import AliasChoices, AnyHttpUrl, Field, field_validator

# Local
import streamlit_passwordless.database as db
from streamlit_passwordless import exceptions
from streamlit_passwordless.bitwarden_passwordless import BITWARDEN_PASSWORDLESS_API_URL
from streamlit_passwordless.models import BaseModel

logger = logging.getLogger(__name__)

# Config keys
STP_SECRETS_SECTION = 'streamlit-passwordless'
STP_BWP_PUBLIC_KEY = 'STP_BWP_PUBLIC_KEY'
STP_BWP_PRIVATE_KEY = 'STP_BWP_PRIVATE_KEY'
STP_BWP_URL = 'STP_BWP_URL'
STP_DB_URL = 'STP_DB_URL'


class ConfigManager(BaseModel):
    r"""Handles the configuration for running Streamlit Passwordless apps.

    Parameters
    ----------
    bwp_public_key : str
        The public key of Bitwarden Passwordless.

    bwp_private_key : str
        The private key of Bitwarden Passwordless.

    bwp_url : pydantic.AnyHttpUrl or str, default AnyHttpUrl('https://v4.passwordless.dev')
        The base url of the backend API of Bitwarden Passwordless. Specify this url
        if you are self-hosting Bitwarden Passwordless.

    db_url : str or sqlalchemy.URL, default 'sqlite:///streamlit_passwordless.db'
        The SQLAlchemy database url of the Streamlit Passwordless user database.
    """

    bwp_public_key: str = Field(validation_alias=AliasChoices('bwp_public_key', STP_BWP_PUBLIC_KEY))
    bwp_private_key: str = Field(
        validation_alias=AliasChoices('bwp_private_key', STP_BWP_PRIVATE_KEY)
    )
    bwp_url: AnyHttpUrl = Field(
        default=BITWARDEN_PASSWORDLESS_API_URL,
        validation_alias=AliasChoices('bwp_url', STP_BWP_URL),
    )
    db_url: str | db.URL = Field(
        default='sqlite:///streamlit_passwordless.db',
        validate_default=True,
        validation_alias=AliasChoices('db_url', STP_DB_URL),
    )

    @field_validator('db_url')
    @classmethod
    def validate_url(cls, url: str | db.URL) -> db.URL:
        r"""Validate the database url."""

        try:
            return db.create_db_url(url)
        except exceptions.DatabaseInvalidUrlError as e:
            raise ValueError(f'{type(e).__name__} : {str(e)}') from None

    @classmethod
    def load(cls) -> Self:
        r"""Load the configuration for a Streamlit Passwordless application.

        The configuration can be loaded from environment variables or Streamlit secrets.
        Values from environment variables will override Streamlit secrets. The Streamlit
        secrets can be defined in "~/.streamlit/secrets.toml" or "./.streamlit/secrets.toml",
        where config keys in the second file will take precedence over the first.

        Returns
        -------
        streamlit_passwordless.ConfigManager
            The loaded configuration.

        Raises
        ------
        streamlit_passwordless.StreamlitPasswordlessError
            If the required configuration could not be found or was invalid.
        """

        config_dict = dict(st.secrets.get(STP_SECRETS_SECTION, {}))

        config_mapping = {
            'db_url': STP_DB_URL,
            'bwp_public_key': STP_BWP_PUBLIC_KEY,
            'bwp_private_key': STP_BWP_PRIVATE_KEY,
            'bwp_url': STP_BWP_URL,
        }

        config_dict |= {
            config_key: value
            for config_key, config_key_name in config_mapping.items()
            if (value := os.getenv(config_key_name)) is not None
        }

        return cls.model_validate(config_dict)

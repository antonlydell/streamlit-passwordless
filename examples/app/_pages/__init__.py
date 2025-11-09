r"""The pages of the Streamlit Passwordless multi-page demo app."""

from enum import StrEnum


class Pages(StrEnum):
    r"""The pages of the app."""

    ADMIN = '_pages/admin.py'
    HOME = '_pages/home.py'
    REGISTER_AND_SIGN_IN = '_pages/register_and_sign_in.py'

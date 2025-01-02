r"""The Streamlit Passwordless administration web app."""

# Local
from .config import setup
from .pages.init import init_page

# The Public API
__all__ = ['init_page', 'setup']

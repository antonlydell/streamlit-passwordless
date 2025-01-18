r"""The Streamlit Passwordless administration web app."""

# Local
from .config import load_config, setup
from .pages.admin import admin_page
from .pages.init import init_page

# The Public API
__all__ = ['admin_page', 'init_page', 'load_config', 'setup']

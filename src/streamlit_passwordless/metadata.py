"""Metadata about the streamlit-passwordless package."""

# Standard library
from datetime import date

__versiontuple__ = (0, 19, 0)
"""The version of streamlit-passwordless in a comparable form.
Adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_
(MAJOR.MINOR.PATCH).
"""

__version__ = '.'.join(str(x) for x in __versiontuple__)
"""The streamlit-passwordless version string."""

__releasedate__ = date(2026, 8, 8)
"""The release date of the version specified in :data:`__versiontuple__`."""

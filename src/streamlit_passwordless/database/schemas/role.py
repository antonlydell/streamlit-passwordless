r"""The schemas for the role model."""

# Standard library

# Third party

# Local
from .core import SchemaBaseModel


class RoleCreate(SchemaBaseModel):
    r"""The schema for creating a new role.

    Parameters
    ----------
    name : str
        The name of the role.

    rank : int
        The rank of the role. A role with a higher rank has more privileges. Used
        for comparing roles against one another. Two roles may have the same rank.

    description : str or None, default None
        A description of the role.
    """

    name: str
    rank: int
    description: str | None = None

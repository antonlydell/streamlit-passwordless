r"""The core functionality of the schema models."""

# Standard library

# Third party
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, ValidationError

# Local
from streamlit_passwordless import exceptions


class SchemaBaseModel(PydanticBaseModel):
    r"""The BaseModel that all schema models will inherit from."""

    model_config = ConfigDict(from_attributes=True)

    def __init__(self, **kwargs) -> None:
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            raise exceptions.StreamlitPasswordlessError(str(e)) from None

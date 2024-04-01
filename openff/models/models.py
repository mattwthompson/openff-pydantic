from openff.models._pydantic import BaseModel
from openff.models.types import custom_quantity_encoder, json_loader
from openff.units import Quantity


class DefaultModel(BaseModel):
    """A custom Pydantic model used by other components."""

    model_config = {
        "json_encoders": {
            Quantity: custom_quantity_encoder,
        },
        "json_loads": json_loader,  # removed in V2, not sure where this went
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
    }

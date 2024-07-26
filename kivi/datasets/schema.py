from numpy.typing import NDArray
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


__all__ = ["MakeDataOutput"]


class MakeDataOutput(BaseModel):
    """"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    x_train: Optional[NDArray] = Field(default=None, description="")
    y_train: Optional[NDArray] = Field(default=None, description="")
    x_test: Optional[NDArray] = Field(default=None, description="")
    y_test: Optional[NDArray] = Field(default=None, description="")

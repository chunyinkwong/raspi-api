from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from .layer_properties import (
    ArcProperties,
    CircleProperties,
    ImageProperties,
    PenProperties,
    RectangleProperties,
)

LayerType = Literal["rectangle", "circle", "pen", "arc", "image"]
LayerProperties = Union[
    RectangleProperties, CircleProperties, PenProperties, ArcProperties, ImageProperties
]


class LayerBase(BaseModel):
    type: LayerType
    properties: LayerProperties


class LayerCreate(LayerBase):
    pass


class Layer(LayerBase):
    id: str
    project_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ImageAdjustments(BaseModel):
    contrast: Optional[float] = Field(None, ge=0, le=2.0, description="Contrast adjustment (0-2)")
    brightness: Optional[float] = Field(None, ge=0, le=2.0, description="Brightness adjustment (0-2)")
    sharpness: Optional[float] = Field(None, ge=0, le=2.0, description="Sharpness adjustment (0-2)")

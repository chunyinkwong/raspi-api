from typing import Optional

from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class ColorProps(BaseModel):
    color: str = Field(..., pattern="^#[0-9a-fA-F]{6}$", description="Hex color code")
    # opacity: float = Field(1.0, ge=0, le=1, description="Opacity level")


class RectangleProperties(Position, ColorProps):
    width: float = Field(..., gt=0, description="Width in pixels")
    height: float = Field(..., gt=0, description="Height in pixels")
    # rotation: float = Field(0, description="Rotation in degrees")


class CircleProperties(Position, ColorProps):
    radius: float = Field(..., gt=0, description="Radius in pixels")


class Point(BaseModel):
    x: float
    y: float


class PenProperties(ColorProps):
    points: list[Point] = Field(..., min_items=2, description="List of points")
    stroke_width: float = Field(1.0, gt=0, description="Stroke width in pixels")


class ArcProperties(ColorProps, Position):
    radius: float = Field(..., gt=0, description="Radius in pixels")
    start_angle: float = Field(..., description="Start angle in degrees")
    end_angle: float = Field(..., description="End angle in degrees")
    stroke_width: float = Field(1.0, gt=0, description="Stroke width in pixels")


class ImageProperties(Position):
    path: str = Field(..., description="Path to uploaded image")
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    contrast: float = Field(1.0, ge=0, le=2.0)
    brightness: float = Field(1.0, ge=0, le=2.0)
    sharpness: float = Field(1.0, ge=0, le=2.0)

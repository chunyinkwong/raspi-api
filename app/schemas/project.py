from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .layer import Layer
from .util import IdModel


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    width: Optional[int] = 800
    height: Optional[int] = 600


class ProjectList(ProjectBase, IdModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "01HRBK8YNPXN5WK0Q23BACDMR5",
                "name": "My Project",
                "description": "A sample project",
                "created_at": "2024-02-20T12:00:00Z",
                "updated_at": "2024-02-20T12:00:00Z",
            }
        }


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase, IdModel):
    created_at: datetime
    updated_at: Optional[datetime] = None
    layers: list[Layer] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "01HRBK8YNPXN5WK0Q23BACDMR5",
                "name": "My Project",
                "description": "A sample project",
                "created_at": "2024-02-20T12:00:00Z",
                "updated_at": "2024-02-20T12:00:00Z",
                "layers": [],
            }
        }


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    width: int | None = None
    height: int | None = None

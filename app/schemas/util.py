from pydantic import BaseModel, Field
from ulid import ULID


class IdModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ULID()), pattern="^[0-9A-HJ-KM-NP-Z]{26}$")

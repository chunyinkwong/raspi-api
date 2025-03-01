from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ulid import ULID

from app.core.database import Base


class Layer(Base):
    __tablename__ = "layers"

    id = Column(String(26), primary_key=True, index=True, default=lambda: str(ULID()))
    project_id = Column(String(26), ForeignKey("projects.id", ondelete="CASCADE"))
    type = Column(String)
    properties = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="layers")

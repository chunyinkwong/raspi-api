from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ulid import ULID

from app.core.database import Base
from app.models.layer import Layer


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(26), primary_key=True, index=True, default=lambda: str(ULID()))
    name = Column(String)
    description = Column(String, nullable=True)
    owner = Column(
        String, ForeignKey("users.username"), nullable=False, index=True
    )
    width = Column(Integer, default=800)
    height = Column(Integer, default=600)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    layers = relationship("Layer", back_populates="project", cascade="all, delete-orphan")


@event.listens_for(Layer, "after_insert")
@event.listens_for(Layer, "after_update")
@event.listens_for(Layer, "after_delete")
def update_project_timestamp(_mapper, connection, target):
    """Update project's updated_at timestamp when layers change"""
    connection.execute(
        Project.__table__.update().where(Project.id == target.project_id).values(updated_at=func.now())
    )

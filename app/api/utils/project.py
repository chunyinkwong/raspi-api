from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project as ProjectModel
from app.models.user import User as UserModel


def fetch_owned_project(db: Session, project_id: str, current_user: UserModel) -> ProjectModel:
    """Get a project and verify ownership."""
    project = (
        db.query(ProjectModel)
        .filter(ProjectModel.id == project_id, ProjectModel.owner == current_user.username)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

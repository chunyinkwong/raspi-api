from io import BytesIO
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session, noload

from app.api.deps import get_current_user, get_db
from app.api.utils.image import render_image
from app.api.utils.project import fetch_owned_project
from app.models.project import Project as ProjectModel
from app.models.user import User as UserModel
from app.schemas.project import Project, ProjectCreate, ProjectList, ProjectUpdate

router = APIRouter()


@router.get("/projects", response_model=list[ProjectList])
async def get_my_projects(
    current_user: Annotated[UserModel, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
):
    """
    Retrieve all projects belonging to the authenticated user (without layers).
    """
    projects = (
        db.query(ProjectModel)
        .options(noload(ProjectModel.layers))
        .filter(ProjectModel.owner == current_user.username)
        .all()
    )
    return projects


@router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Get detailed information about a specific project, including its layers.
    """
    project = (
        db.query(ProjectModel)
        .filter(ProjectModel.id == project_id, ProjectModel.owner == current_user.username)
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.post("/projects", response_model=Project)
async def create_project(
    project: ProjectCreate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create a new project.
    """
    db_project = ProjectModel(**project.model_dump(), owner=current_user)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Delete a project.
    """
    project = fetch_owned_project(db, project_id, current_user)
    db.delete(project)
    db.commit()

    return Response(status_code=204)


@router.get(
    "/projects/{project_id}/render",
    response_class=Response,
    responses={
        200: {
            "content": {
                "image/png": {},
                "image/jpeg": {},
            },
            "description": "Returns the rendered project image",
        }
    },
)
async def render_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
    file_extension: Optional[str] = None,
    accept: Annotated[str | None, Header()] = None,
):
    """
    Render a project and return it as an image file.
    Format is determined by Accept header or file_extension query parameter.
    Supported formats: image/png, image/jpeg
    """
    project = fetch_owned_project(db, project_id, current_user)

    format_from_accept = None
    if accept:
        if "image/png" in accept:
            format_from_accept = "png"
        elif "image/jpeg" in accept:
            format_from_accept = "jpg"

    chosen_format = (file_extension or format_from_accept or "png").lower()

    valid_formats = ["png", "jpg", "jpeg"]
    if chosen_format not in valid_formats:
        raise HTTPException(
            status_code=406,
            detail="Unsupported format. Supported formats: png, jpg, jpeg",
        )

    sorted_layers = sorted(project.layers, key=lambda x: x.created_at)

    img = render_image(project, sorted_layers)

    if chosen_format in ["jpg", "jpeg"]:
        img = img.convert("RGB")

    img_byte_arr = BytesIO()
    img.save(
        img_byte_arr,
        format="PNG" if chosen_format == "png" else "JPEG",
        quality=95 if chosen_format in ["jpg", "jpeg"] else None,
    )
    img_byte_arr = img_byte_arr.getvalue()

    content_type = "image/png" if chosen_format == "png" else "image/jpeg"

    return Response(content=img_byte_arr, media_type=content_type)


@router.patch("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Update project details (name, description, dimensions).
    """
    project = fetch_owned_project(db, project_id, current_user)

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project

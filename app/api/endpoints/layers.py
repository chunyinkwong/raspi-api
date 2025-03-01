import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.utils.project import fetch_owned_project
from app.models.layer import Layer as LayerModel
from app.models.user import User as UserModel
from app.schemas.layer import ImageAdjustments, Layer
from app.schemas.layer_properties import (
    ArcProperties,
    CircleProperties,
    PenProperties,
    RectangleProperties,
)

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 8 * 1024 * 1024


@router.post("/projects/{project_id}/upload")
async def upload_image(
    project_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File()] = ...,
):
    """Upload an image and create an image layer."""
    file_size = 0
    contents = await file.read()
    file_size = len(contents)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    await file.seek(0)

    project = fetch_owned_project(db, project_id, current_user)

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR.joinpath(f"{project_id}_{safe_filename}")

    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail="A file with this name already exists. Please rename the file and try again.",
        )

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    layer = LayerModel(
        project_id=project.id,
        type="image",
        properties={
            "path": str(file_path),
            "x": 0,
            "y": 0,
            "contrast": 1.0,
            "brightness": 1.0,
            "sharpness": 1.0,
        },
    )

    db.add(layer)
    db.commit()
    db.refresh(layer)
    return layer


@router.delete("/projects/{project_id}/{layer_id}", status_code=204)
async def delete_layer(
    project_id: str,
    layer_id: str,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Delete a specific layer from the project.
    """
    project = fetch_owned_project(db, project_id, current_user)

    layer = (
        db.query(LayerModel).filter(LayerModel.id == layer_id, LayerModel.project_id == project.id).first()
    )
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    db.delete(layer)
    db.commit()
    return Response(status_code=204)


@router.patch("/projects/{project_id}/{layer_id}", response_model=Layer)
async def patch_layer(
    project_id: str,
    layer_id: str,
    adjustments: ImageAdjustments,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Patch layer properties. Currently supports updating image adjustments
    (contrast, brightness, sharpness) for image layers.
    """
    project = fetch_owned_project(db, project_id, current_user)

    layer = (
        db.query(LayerModel).filter(LayerModel.id == layer_id, LayerModel.project_id == project.id).first()
    )

    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")

    if layer.type != "image":
        raise HTTPException(status_code=400, detail="Only image layers can be adjusted")

    properties = dict(layer.properties)

    if adjustments.contrast is not None:
        properties["contrast"] = adjustments.contrast
    if adjustments.brightness is not None:
        properties["brightness"] = adjustments.brightness
    if adjustments.sharpness is not None:
        properties["sharpness"] = adjustments.sharpness

    layer.properties = properties

    db.commit()
    db.refresh(layer)
    return layer


@router.post("/projects/{project_id}/layers/rectangle", response_model=Layer)
async def add_rectangle_layer(
    project_id: str,
    properties: RectangleProperties,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Add a new rectangle layer to the project."""
    project = fetch_owned_project(db, project_id, current_user)

    db_layer = LayerModel(project_id=project.id, type="rectangle", properties=properties.model_dump())
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    return db_layer


@router.post("/projects/{project_id}/layers/circle", response_model=Layer)
async def add_circle_layer(
    project_id: str,
    properties: CircleProperties,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Add a new circle layer to the project."""
    project = fetch_owned_project(db, project_id, current_user)

    db_layer = LayerModel(project_id=project.id, type="circle", properties=properties.model_dump())
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    return db_layer


@router.post("/projects/{project_id}/layers/pen", response_model=Layer)
async def add_pen_layer(
    project_id: str,
    properties: PenProperties,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Add a new pen layer to the project."""
    project = fetch_owned_project(db, project_id, current_user)

    db_layer = LayerModel(project_id=project.id, type="pen", properties=properties.model_dump())
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    return db_layer


@router.post("/projects/{project_id}/layers/arc", response_model=Layer)
async def add_arc_layer(
    project_id: str,
    properties: ArcProperties,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Add a new arc layer to the project."""
    project = fetch_owned_project(db, project_id, current_user)

    db_layer = LayerModel(project_id=project.id, type="arc", properties=properties.model_dump())
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    return db_layer

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, is_admin
from app.core.security import create_jwt_token
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/auth/register", response_model=UserSchema)
def register_user(
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    is_admin: Annotated[bool, Depends(is_admin)],
) -> Any:
    """
    Register a new user (admin only).
    """

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admins can create new users",
        )

    user = (
        db.query(User).filter((User.email == user_in.email) | (User.username == user_in.username)).first()
    )
    if user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    db_user = User(
        email=user_in.email,
        username=user_in.username,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/auth/make_key", response_model=Token)
async def make_key(
    username: str, is_admin: Annotated[bool, Depends(is_admin)], db: Annotated[Session, Depends(get_db)]
) -> Any:
    """
    Create a JWT token for a user (admin only).
    """
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admins can create tokens",
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_jwt_token(data={"sub": user.username}, expires_delta=None)
    return Token(access_token=access_token, token_type="jwt")

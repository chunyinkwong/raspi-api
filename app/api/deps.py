from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_jwt_token
from app.models.user import User as UserModel
from app.schemas.user import User

api_key_header = APIKeyHeader(name="X-API-Key")


async def get_api_key(api_key: Annotated[str, Security(api_key_header)]) -> str:
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
    return api_key


async def get_current_user(
    db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(get_api_key)]
) -> User:
    """Verify JWT token and get current user"""
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def is_admin(api_key: Annotated[str, Depends(get_api_key)]) -> bool:
    return compare_digest(api_key, settings.ADMIN_API_KEY)

from fastapi import FastAPI

from app.api.endpoints import auth, layers, projects
from app.core.config import settings
from app.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Include routers
app.include_router(projects.router, prefix=settings.API_V1_STR, tags=["projects"])
app.include_router(layers.router, prefix=settings.API_V1_STR, tags=["layers"])
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

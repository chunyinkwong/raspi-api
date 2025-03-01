from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Photo Editing API"

    # Database
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./photo_editing.db"

    # Security
    SECRET_KEY: str
    ADMIN_API_KEY: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Masjid Management System"
    API_V1_STR: str = "/api/v1"
    
    # Database
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./masjid.db"

    # Security
    SECRET_KEY: str = "super_secret_key_please_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        env_file = ".env"

settings = Settings()

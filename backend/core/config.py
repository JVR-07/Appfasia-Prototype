from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL
    database_url: str

    # ArcadeDB
    arcadedb_bolt: str
    arcadedb_user: str
    arcadedb_database: str
    arcadedb_root_password: str

    # Redis
    redis_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 30

    # Azure STT
    azure_speech_key: str = "mock"
    azure_speech_region: str = "eastus"

    # Gemini
    gemini_api_key: str = ""

    # App
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

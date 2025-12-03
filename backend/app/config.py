from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

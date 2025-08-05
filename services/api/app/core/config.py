from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/database"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MeatyPrompts"

    class Config:
        env_file = ".env"

settings = Settings()

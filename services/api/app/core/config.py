from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MeatyPrompts"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

settings = Settings()

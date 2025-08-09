from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_TEST: str
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MeatyPrompts"
    CLERK_JWT_VERIFICATION_KEY: str
    CLERK_WEBHOOK_SECRET: str
    CLERK_SECRET_KEY: str | None = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()

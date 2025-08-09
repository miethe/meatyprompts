from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_TEST: str
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MeatyPrompts"
    AUTH_COOKIE_NAME: str = "mp_session"
    AUTH_COOKIE_DOMAIN: str | None = None
    AUTH_SIGNING_SECRET: str
    FF_AUTH_MAGIC_LINK: bool = False
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()

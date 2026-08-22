from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    initial_admin_email: str = ""
    frontend_origin: str = "http://localhost:5173"
    booking_auto_cancel_seconds: int = 600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

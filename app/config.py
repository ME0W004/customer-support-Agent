from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GEMINI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    GMAIL_REFRESH_TOKEN: str
    SUPPORT_EMAIL: str = "madiakrami1384@gmail.com"
    POLL_INTERVAL_SECONDS: int = 30
    APP_ENV: str = "development"


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://feedy:feedy@localhost:5432/feedy"
    database_url_sync: str = "postgresql+psycopg2://feedy:feedy@localhost:5432/feedy"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173"
    secret_key: str = "change-me-to-a-random-secret"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    rate_limit_enabled: bool = True
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_starter: str = ""
    stripe_price_pro: str = ""
    stripe_price_business: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@feedy.pl"
    smtp_from_name: str = "Feedy"
    app_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

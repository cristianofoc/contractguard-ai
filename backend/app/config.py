"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe configuration management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/contractguard"

    # Auth / JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Storage (Supabase or S3)
    STORAGE_BUCKET: str = "contractguard-contracts"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Pricing / usage limits
    FREE_ANALYSES_LIMIT: int = 1
    PAY_PER_USE_PRICE_CENTS: int = 300

    # App metadata
    APP_NAME: str = "ContractGuard AI"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton settings object used throughout the app
settings = Settings()

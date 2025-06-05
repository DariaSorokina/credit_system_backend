from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/credit_system"
    REDIS_URL: str = "redis://redis:6379/0"
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    EMAIL_FROM: str = "noreply@creditsystem.com"
    SECRET_KEY: str = "secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
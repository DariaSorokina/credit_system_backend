from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Явно указываем использование psycopg2
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", 
    "postgresql+psycopg2://"
) if not settings.DATABASE_URL.startswith("postgresql+psycopg2://") else settings.DATABASE_URL

# Пул соединений с настройками
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Рекомендуется для FastAPI
)

Base = declarative_base()

def get_db():
    """Генератор сессий для Dependency Injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
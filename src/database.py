from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import  declarative_base, sessionmaker

# URL базы данных
DATABASE_URL = "sqlite+aiosqlite:///./src/app.db"


def get_async_engine(database_url: str):
    """Создает и возвращает test_async_engine для заданного URL базы данных."""
    return create_async_engine(database_url, echo=True)


def get_async_session(_async_engine):
    """Создает и возвращает async_session для заданного _async_engine."""
    return sessionmaker(bind=_async_engine, class_=AsyncSession, expire_on_commit=False)


# Создаем test_async_engine
async_engine = get_async_engine(database_url=DATABASE_URL)

# Создаем async_session
async_session = get_async_session(_async_engine=async_engine)

# Базовый класс для моделей
Base = declarative_base()

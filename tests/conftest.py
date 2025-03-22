import pytest
from fastapi.testclient import TestClient

from src.database import Base, get_async_engine, get_async_session
from src.main import app as main_app
from src.main import get_db

# Устанавливаем URL для тестовой базы данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_app.db"

# Создаем test_async_engine для тестов
test_async_engine = get_async_engine(TEST_DATABASE_URL)

# Создаем async_session для тестов
test_async_session = get_async_session(test_async_engine)


# Фикстура для создания тестовой базы данных
@pytest.fixture(scope="module", autouse=True)
async def test_db():
    # Создаем тестовую базу данных
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем тестовую базу данных после завершения тестов
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Фикстура для асинхронной сессии
@pytest.fixture(scope="module")
async def db_session():
    async with test_async_session() as session:
        yield session


# Фикстура для переопределения зависимости get_db
@pytest.fixture(scope="module")
def override_get_db(db_session):
    async def _override_get_db():
        yield db_session

    return _override_get_db


# Фикстура для создания тестового приложения
@pytest.fixture(scope="module")
def app(override_get_db):
    # Переопределяем зависимость get_db в приложении
    main_app.dependency_overrides[get_db] = override_get_db
    return main_app


# Фикстура для синхронного клиента (TestClient)
@pytest.fixture(scope="module")
def client(app):
    return TestClient(app)

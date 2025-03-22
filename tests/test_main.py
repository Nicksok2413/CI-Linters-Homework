import pytest
from sqlalchemy import select

from src.models import Recipe


# Тест для получения всех рецептов
@pytest.mark.asyncio
async def test_get_all_recipes(client, db_session):
    # Добавляем тестовые данные
    recipe_1 = Recipe(
        dish_name="Test Dish 1",
        cooking_time=30,
        ingredients="Ing1, Ing2",
        description="Test Description 1",
    )
    recipe_2 = Recipe(
        dish_name="Test Dish 2",
        cooking_time=40,
        ingredients="Ing3, Ing4",
        description="Test Description 2",
    )
    db_session.add(recipe_1)
    db_session.add(recipe_2)
    await db_session.commit()

    # Выполняем запрос
    response = client.get("/recipes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["dish_name"] == "Test Dish 1"
    assert data[1]["dish_name"] == "Test Dish 2"


# Тест для получения рецепта по ID
@pytest.mark.asyncio
async def test_get_recipe_by_id(client, db_session):
    # Добавляем тестовые данные
    recipe = Recipe(
        dish_name="Test Dish",
        cooking_time=30,
        ingredients="Ing1, Ing2",
        description="Test Description",
    )
    db_session.add(recipe)
    await db_session.commit()

    # Выполняем запрос
    response = client.get(f"/recipes/{recipe.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["dish_name"] == "Test Dish"
    assert data["cooking_time"] == 30
    assert data["views"] == 1  # Просмотры увеличились на 1


# Тест для добавления нового рецепта
@pytest.mark.asyncio
async def test_add_recipe(client, db_session):
    # Данные для нового рецепта
    new_recipe = {
        "dish_name": "New Dish",
        "cooking_time": 50,
        "ingredients": "Ing5, Ing6",
        "description": "New Description",
    }

    # Выполняем запрос
    response = client.post("/recipes", json=new_recipe)
    assert response.status_code == 200
    data = response.json()
    assert data["dish_name"] == "New Dish"
    assert data["cooking_time"] == 50

    # Проверяем, что рецепт добавлен в базу данных
    result = await db_session.execute(select(Recipe).filter(Recipe.id == data["id"]))
    recipe = result.scalars().first()
    assert recipe is not None
    assert recipe.dish_name == "New Dish"


# Тест для случая, когда рецепт не найден
@pytest.mark.asyncio
async def test_get_recipe_not_found(client):
    response = client.get("/recipes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"

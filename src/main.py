from contextlib import asynccontextmanager
from typing import AsyncIterator, AsyncGenerator, Sequence

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database import Base, async_engine, async_session
from src.models import Recipe
from src.schemas import RecipeIn, RecipeOut, RecipesOut


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Код, выполняемый при запуске приложения
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Код, выполняемый при завершении работы приложения
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@app.get(
    "/recipes",
    response_model=list[RecipesOut],
    summary="Get all recipes",
    description="Returns a list of recipes sorted by views & cooking time.",
)
async def get_all_recipes(db: AsyncSession = Depends(get_db)) -> Sequence[Recipe]:
    result = await db.execute(
        select(Recipe).order_by(Recipe.views.desc(), Recipe.cooking_time)
    )
    recipes = result.scalars().all()
    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeOut,
    summary="Get recipe by ID",
    description="Returns detailed information about a specific recipe.",
)
async def get_recipe_by_id(
        recipe_id: int, db: AsyncSession = Depends(get_db)
) -> Recipe:
    result = await db.execute(select(Recipe).filter(Recipe.id == recipe_id))
    recipe = result.scalars().one_or_none()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Обновляем количество просмотров в БД
    await db.execute(
        update(Recipe)
        .where(Recipe.id == recipe_id)
        .values(views=Recipe.views + 1)
    )
    await db.commit()

    # Повторно загружаем обновленный рецепт
    result = await db.execute(select(Recipe).filter(Recipe.id == recipe_id))
    updated_recipe = result.scalars().one()

    return updated_recipe


@app.post(
    "/recipes",
    response_model=RecipeOut,
    summary="Add a new recipe",
    description="Creates a new recipe in the database.",
)
async def add_recipe(recipe: RecipeIn, db: AsyncSession = Depends(get_db)) -> Recipe:
    new_recipe = Recipe(**recipe.model_dump())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe

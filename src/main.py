from typing import AsyncIterator, Sequence
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager

from src.database import async_engine, async_session, Base
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


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.get(
    "/recipes",
    response_model=list[RecipesOut],
    summary="Get all recipes",
    description="Returns a list of all recipes sorted by views and cooking time.",
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
    result = await db.execute(select(Recipe).filter(recipe_id == Recipe.id))
    recipe = result.scalars().one_or_none()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)
    return recipe


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

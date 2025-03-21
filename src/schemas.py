from pydantic import BaseModel


class BaseRecipe(BaseModel):
    dish_name: str
    cooking_time: int
    ingredients: str
    description: str


class RecipeIn(BaseRecipe):
    ...


class RecipeOut(BaseRecipe):
    id: int
    views: int

    class ConfigDict:
        from_attributes = True


class RecipesOut(BaseModel):
    dish_name: str
    cooking_time: int
    views: int

    class ConfigDict:
        from_attributes = True

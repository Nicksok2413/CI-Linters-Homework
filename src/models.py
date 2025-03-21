from sqlalchemy import Column, Integer, String, Text

from src.database import Base


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String, index=True)
    views = Column(Integer, default=0)
    cooking_time = Column(Integer, nullable=False)
    ingredients = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

from sqlalchemy import String, Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    steps = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(TIMESTAMP)

    author = relationship("User", back_populates="recipes")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False)

    recipes = relationship("Recipe", back_populates="author")

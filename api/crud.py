from typing import Optional
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session
from argon2 import PasswordHasher

from . import models, schemas

ph = PasswordHasher()


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=ph.hash(user.password.get_secret_value()),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_or_create_user_token(
    db: Session, user_id: int, token: schemas.Token
) -> models.OAuth2Token:
    # See if existing user token exists.
    existing_token = (
        db.query(models.OAuth2Token)
        .filter(
            models.OAuth2Token.user_id == user_id, models.OAuth2Token.name == token.name
        )
        .first()
    )
    if existing_token:
        db_token = existing_token
        setattr(db_token, "name", token.name)
        setattr(db_token, "token_type", token.token_type)
        setattr(db_token, "access_token", token.access_token)
        setattr(db_token, "expires_at", token.expires_at)

    else:
        db_token = models.OAuth2Token(
            user_id=user_id,
            name=token.name,
            token_type=token.token_type,
            access_token=token.access_token,
            expires_at=token.expires_at,
        )
        db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()


def get_recipes(
    db: Session, recipe_params: schemas.RecipeSearch, author_id: Optional[int] = None
) -> schemas.PaginatedRecipes:
    recipe_qs = db.query(models.Recipe)

    # Filter by author, if required.
    if author_id:
        recipe_qs = recipe_qs.filter(models.Recipe.author_id == author_id)
    total_recipe_count = recipe_qs.count()
    max_page = max(
        total_recipe_count // recipe_params.per_page
        + (
            total_recipe_count % recipe_params.per_page > 1 & 1
        ),  # Add one if there is any remainder
        1,
    )
    offset = recipe_params.per_page * (recipe_params.page - 1)
    recipe_qs = recipe_qs.limit(recipe_params.per_page).offset(offset)
    return schemas.PaginatedRecipes(
        page=recipe_params.page,
        max_page=max_page,
        per_page=recipe_params.per_page,
        result_count=total_recipe_count,
        data=[schemas.RecipeInDB.from_orm(recipe) for recipe in recipe_qs],
    )


def create_recipe(db: Session, author_id: int, recipe: schemas.RecipeCreate):
    db_recipe = models.Recipe(
        name=recipe.name,
        author_id=author_id,
        created_at=datetime.utcnow(),
    )
    db.add(db_recipe)
    db.commit()
    return db_recipe


def update_recipe(db: Session, recipe: models.Recipe, edit: schemas.RecipeEdit):
    setattr(recipe, "name", edit.name)
    db.commit()
    return recipe


def get_ingredient(db: Session, ingredient_id: int):
    ingredient = db.query(models.RecipeIngredient).get(ingredient_id)
    return ingredient


def update_ingredient(
    db: Session, ingredient: models.RecipeIngredient, edit: schemas.RecipeIngredientEdit
):
    setattr(ingredient, "content", edit.content)
    db.commit()


def delete_ingredient(db: Session, ingredient: models.RecipeIngredient):
    # Delete the ingredient and shift the positions of the ingredient
    # with a higher position down one.
    empty_position = ingredient.position
    recipe_id = ingredient.recipe_id
    db.delete(ingredient)    

    (  # Decrement the position of any procededing ingredients.
        db.query(models.RecipeIngredient)
        .filter(models.RecipeIngredient.recipe_id == recipe_id)
        .filter(models.RecipeIngredient.position > empty_position)
        .update(
            {models.RecipeIngredient.position: models.RecipeIngredient.position - 1}
        )
    )
    db.commit()


def append_recipe_ingredient(
    db: Session, recipe_id: int, ingredient: schemas.RecipeIngredientCreate
):
    ingredient_count = (
        db.query(models.RecipeIngredient)
        .filter(models.RecipeIngredient.recipe_id == recipe_id)
        .count()
    )
    db_ingredient = models.RecipeIngredient(
        **ingredient.dict(), recipe_id=recipe_id, position=ingredient_count
    )
    db.add(db_ingredient)
    db.commit()
    return db_ingredient


def get_step(db: Session, step_id: int):
    return db.query(models.RecipeStep).get(step_id)


def update_step(db: Session, step: models.RecipeStep, edit: schemas.RecipeStepEdit):
    setattr(step, "content", edit.content)
    db.commit()
    return step


def delete_step(db: Session, step: models.RecipeStep):
    empty_position = step.position
    recipe_id = step.recipe_id
    
    db.delete(step)    

    (  # Decrement the position of any procededing steps.
        db.query(models.RecipeStep)
        .filter(models.RecipeStep.recipe_id == recipe_id)
        .filter(models.RecipeStep.position > empty_position)
        .update(
            {models.RecipeStep.position: models.RecipeStep.position - 1}
        )
    )
    db.commit()
    db.delete(step)
    db.commit()


def append_recipe_step(db: Session, recipe_id: int, step: schemas.RecipeStepCreate):
    step_count = (
        db.query(models.RecipeStep)
        .filter(models.RecipeStep.recipe_id == recipe_id)
        .count()
    )
    db_step = models.RecipeStep(**step.dict(), recipe_id=recipe_id, position=step_count)
    db.add(db_step)
    db.commit()
    return db_step

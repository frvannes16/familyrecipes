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
    db: Session, recipe_params: schemas.RecipeSearch
) -> schemas.PaginatedRecipes:
    recipe_count = db.query(models.Recipe).count()
    max_page = max(
        recipe_count // recipe_params.per_page
        + (
            recipe_count % recipe_params.per_page > 1 & 1
        ),  # Add one if there is any remainder
        1,
    )
    offset = recipe_params.per_page * (recipe_params.page - 1)
    recipes = db.query(models.Recipe).limit(recipe_params.per_page).offset(offset)
    return schemas.PaginatedRecipes(
        page=recipe_params.page,
        max_page=max_page,
        per_page=recipe_params.per_page,
        result_count=recipe_count,
        data=[schemas.RecipeInDB.from_orm(recipe) for recipe in recipes],
    )

import logging
from logging import config as logging_config
from typing import List

from fastapi import FastAPI, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from api import schemas, crud, auth
from api.database import get_db
from api.cookbooks import generator as cookbook_generator

# setup loggers
logging_config.fileConfig("api/logging.conf", disable_existing_loggers=False)

# setup app
app = FastAPI()

origins = [
    "localhost:8000",
    "https://localhost:8000",
    "https://localhost:3000",
    "localhost:3000",
]  # TODO: make production-ready.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/me/", response_model=schemas.AuthenticatedUser)
async def get_my_user(user: schemas.AuthenticatedUser = Depends(auth.get_current_user)):
    return user


@app.get("/users/{user_id}/", response_model=schemas.User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@app.get("/recipes/", response_model=schemas.PaginatedRecipes)
async def get_recipes(
    params: schemas.RecipeSearch = Depends(),
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_recipes(db=db, recipe_params=params)


@app.post(
    "/recipes/",
    response_model=schemas.RecipeInDB,
)
async def create_user_recipe(
    recipe: schemas.RecipeCreate,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):

    return crud.create_recipe(db, author_id=user.id, recipe=recipe)


@app.post("/recipes/{recipe_id}/", response_model=schemas.RecipeInDB)
async def update_recipe(
    recipe_id: int,
    edit: schemas.RecipeEdit,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Could not find recipe with id {recipe_id}",
        )
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You do not have access to this recipe.",
        )

    recipe = crud.update_recipe(db, recipe, edit)
    return schemas.RecipeInDB.from_orm(recipe)


@app.get("/recipes/{recipe_id}/generate-pdf/")
async def generate_recipe_pdf(
    recipe_id: int,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Could not find recipe with id {recipe_id}",
        )
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="You do not have access to this recipe.",
        )
    recipe_list = [schemas.RecipeInDB.from_orm(recipe)]
    pdf_bytes = cookbook_generator.generate_pdf_from_recipes(recipe_list)
    response = Response(content=pdf_bytes, media_type="application/pdf")
    response.headers.update(
        {"Content-Disposition": "attachment", "filename": "my-recipe.pdf"}
    )
    return response


@app.get("/users/{author_id}/recipes/", response_model=schemas.PaginatedRecipes)
async def get_user_recipes(
    author_id: int,
    params: schemas.RecipeSearch = Depends(),
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    # get author or 404
    if not crud.get_user(db, author_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )
    return crud.get_recipes(db=db, recipe_params=params, author_id=author_id)


@app.get("/recipes/{recipe_id}/", response_model=schemas.RecipeInDB)
async def get_single_recipe(
    recipe_id: int,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    # get recipe
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="recipe does not exist"
        )

    # assert user is author
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="recipe does not belong to user",
        )

    return schemas.RecipeInDB.from_orm(recipe)


@app.post(
    "/recipes/ingredients/{ingredient_id}/",
    response_model=List[schemas.RecipeIngredientInDB],
)
async def update_ingredient(
    ingredient_id: int,
    ingredient_edit: schemas.RecipeIngredientEdit,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    # get ingredient or 404
    ingredient = crud.get_ingredient(db, ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ingredient does not exist"
        )

    if ingredient.recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ingredient does not belong to user",
        )

    # Edit the ingredient
    crud.update_ingredient(db, ingredient, ingredient_edit)
    # Return all of the recipe's ingredients
    return [
        schemas.RecipeIngredientInDB.from_orm(ingredient)
        for ingredient in ingredient.recipe.ingredients
    ]


@app.post(
    "/recipes/{recipe_id}/ingredients/",
    response_model=List[schemas.RecipeIngredientInDB],
)
async def add_ingredient(
    recipe_id: int,
    new_ingredient: schemas.RecipeIngredientCreate,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    # get recipe
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="recipe does not exist"
        )

    # assert user owns recipe
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="recipe does not belong to user",
        )

    # Append the ingredient.
    db_ingredient = crud.append_recipe_ingredient(db, recipe_id, new_ingredient)
    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error",
        )
    return [
        schemas.RecipeIngredientInDB.from_orm(ingredient)
        for ingredient in recipe.ingredients
    ]


@app.post(
    "/recipes/{recipe_id}/steps/",
    response_model=List[schemas.RecipeStepInDB],
)
async def add_step(
    recipe_id: int,
    new_step: schemas.RecipeStepCreate,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    # get recipe
    recipe = crud.get_recipe(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="recipe does not exist"
        )

    # assert user owns recipe
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="recipe does not belong to user",
        )

    # Append the step.
    db_step = crud.append_recipe_step(db, recipe_id, new_step)
    if not db_step:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown server error",
        )
    return [schemas.RecipeStepInDB.from_orm(step) for step in recipe.steps]


app.include_router(auth.router)

# Mount the html staticfile loader so that we don't override other endpoints.
# This is the last URI to resolve.
app.mount("/", StaticFiles(directory="api/html", html=True), name="html")

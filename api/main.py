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

origins = ["*"]  # TODO: make production-ready.

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
    status_code=status.HTTP_201_CREATED,
)
async def create_user_recipe(
    recipe: schemas.RecipeCreate,
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):

    return crud.create_recipe(db, author_id=user.id, recipe=recipe)


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


app.include_router(auth.router)

# Mount the html staticfile loader so that we don't override other endpoints.
# This is the last URI to resolve.
app.mount("/", StaticFiles(directory="api/html", html=True), name="html")

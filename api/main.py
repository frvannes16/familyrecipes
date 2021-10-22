from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from api import schemas, crud, auth
from api.database import get_db

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
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/recipes/", response_model=schemas.PaginatedRecipes)
async def get_recipes(
    params: schemas.RecipeSearch = Depends(),
    user: schemas.AuthenticatedUser = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_recipes(db=db, recipe_params=params)


app.include_router(auth.router)

# Mount the html staticfile loader so that we don't override other endpoints.
# This is the last URI to resolve.
app.mount("/", StaticFiles(directory="api/html", html=True), name="html")

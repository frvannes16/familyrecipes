from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from api import schemas, crud, auth
from api.database import get_db

app = FastAPI()


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


app.include_router(auth.router)

# Mount the html staticfile loader so that we don't override other endpoints.
# This is the last URI to resolve.
app.mount("/", StaticFiles(directory="api/html", html=True), name="html")

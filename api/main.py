from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import schemas, crud
from .database import SessionLocal, engine

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user_id}/", response_model=schemas.User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    if db_user:
        return db_user
    else:
        raise HTTPException(status_code=500, detail="Could not create user")


# Mount the html staticfile loader so that we don't override other endpoints.
# This is the last URI to resolve.
app.mount("/", StaticFiles(directory="api/html", html=True), name="html")

from api.models import OAuth2Token
from datetime import timedelta, datetime
from typing import Optional


from fastapi import Depends, APIRouter, status, Response
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import argon2
from jose import JWTError, jwt

from api import schemas, crud
from api.crud import get_user_by_email
from api.database import get_db
from api.settings import settings
from api.utils import OAuth2PasswordBearerWithCookie

ph = argon2.PasswordHasher()

oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="auth/token/"
)  # define oauth url inside of auth router endpoint domain.


JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 10

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependencies


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> schemas.AuthenticatedUser:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    # Validate that the request token matches the db token.
    db_token: OAuth2Token = user.token
    if db_token and db_token.access_token != token:
        raise credentials_exception

    # Check if the token is expired.
    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Construct response object.
    authenticated_user = schemas.AuthenticatedUser(
        **schemas.User.from_orm(user).dict(),
        token=schemas.Token.from_orm(db_token),
        role=user.role.value,
    )
    return authenticated_user


# Auth Routes


@router.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    if db_user:
        return schemas.User(
            id=db_user.id,
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
        )
    else:
        raise HTTPException(status_code=500, detail="Could not create user")


@router.post(
    "/token/", response_model=schemas.AuthenticationResponse
)  # corresponds to oauth2_scheme tokenUrl
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    authenticated_user = authenticate_user(
        db, form_data.username, schemas.PasswordStr(form_data.password)
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email and password combination",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate and save an OAuth2 token.

    access_token_expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": str(authenticated_user.email),
    }
    if authenticated_user.full_name:
        access_token_data.update({"name": authenticated_user.full_name})

    access_token = create_access_token(
        data=access_token_data, expires_delta=access_token_expires_delta
    )
    expires_at = datetime.utcnow() + access_token_expires_delta
    token = schemas.Token(
        name="OAuth2",
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
    )

    crud.update_or_create_user_token(db, authenticated_user.id, token)

    response.set_cookie(
        key="access_token",
        value=f"bearer {str(access_token)}",
        httponly=not settings.debug,
        secure=not settings.debug,
    )

    return {"access_token": access_token, "token_type": "bearer"}


# Helpers


def authenticate_user(
    db: Session, email: str, password: schemas.PasswordStr
) -> Optional[schemas.User]:
    """Returns a user if the email and password cominbation is correct for this user. None otherwise."""
    user = get_user_by_email(db, email=email)

    if not user:
        # Can't find the user.
        return None

    stored_hash = user.hashed_password

    try:
        ph.verify(stored_hash, password.get_secret_value())
    except argon2.exceptions.VerificationError:
        # hash doesn't match the given password.
        return None

    return schemas.User.from_orm(user)


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    """Creates a JWT with the given data and expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt

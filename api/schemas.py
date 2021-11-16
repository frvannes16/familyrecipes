import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, SecretStr


class PasswordStr(SecretStr):
    """
    Secret Password string with password requirement validation.
    If the password does not fit the password requirements, then the password is invalid.
    PasswordStr inherits from SecretStr, which means that the string cannot be rendered or logged.
    """

    MINIMUM_PASSWORD_LENGTH = 12
    SPECIAL_CHARS = "{}<>,.;:/?[]()!@#$%^&*()~`"

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        for validator in super().__get_validators__():
            yield validator
        yield cls.is_str
        yield cls.satisfies_length_requirement
        yield cls.satisfies_special_char_requirement
        yield cls.satisfies_case_mixture

    @classmethod
    def is_str(cls, password: "PasswordStr") -> "PasswordStr":
        if not isinstance(password.get_secret_value(), str):
            raise TypeError("string required")
        return password

    @classmethod
    def satisfies_length_requirement(cls, password: "PasswordStr") -> "PasswordStr":
        if len(password.get_secret_value()) < cls.MINIMUM_PASSWORD_LENGTH:
            raise ValueError(
                f"Must be longer than {cls.MINIMUM_PASSWORD_LENGTH} characters"
            )
        return password

    @classmethod
    def satisfies_special_char_requirement(
        cls, password: "PasswordStr"
    ) -> "PasswordStr":
        if not any([char in password.get_secret_value() for char in cls.SPECIAL_CHARS]):
            raise ValueError(
                f"Must contain at least one special character: {cls.SPECIAL_CHARS}"
            )
        return password

    @classmethod
    def satisfies_case_mixture(cls, password: "PasswordStr") -> "PasswordStr":
        if password.get_secret_value().lower() == password.get_secret_value():
            raise ValueError(
                f"Must contain a mixture of uppercase and lowercase characters"
            )
        return password


# USER


class Token(BaseModel):
    name: str
    access_token: str
    token_type: str
    expires_at: datetime.datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]


class AuthenticatedUser(UserBase):  # We only need to show the user their own token.
    id: int
    token: Token
    role: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: PasswordStr


class User(UserBase):
    id: int

    class Config:
        orm_mode = True

    @property
    def full_name(self) -> Optional[str]:
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.first_name
        return None


# Auth models


class AuthenticationResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


# RECIPES


class RecipeIngredientBase(BaseModel):
    content: str


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredientEdit(RecipeIngredientBase):
    pass


class RecipeIngredientInDB(RecipeIngredientBase):
    id: int
    recipe_id: int
    position: int

    class Config:
        orm_mode = True


class RecipeStepBase(BaseModel):
    content: str


class RecipeStepCreate(RecipeStepBase):
    pass


class RecipeStepInDB(RecipeStepBase):
    id: int
    recipe_id: int
    position: int

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    name: str


class RecipeCreate(RecipeBase):
    pass


class RecipeEdit(RecipeBase):
    pass


class RecipeInDB(RecipeBase):
    id: int
    created_at: datetime.datetime
    author_id: int
    author: User
    steps: list[RecipeStepInDB]
    ingredients: list[RecipeIngredientInDB]

    class Config:
        orm_mode = True


class RecipeSearch(BaseModel):
    page: int = 1
    per_page: int = 10


class PaginatedRecipes(BaseModel):
    page: int
    per_page: int
    max_page: int
    result_count: int
    data: list[RecipeInDB]

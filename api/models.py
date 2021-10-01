from typing import Optional
import enum

from sqlalchemy import String, Column, Integer, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship

from api.database import Base


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


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
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role: Column[Role] = Column(
        Enum(Role),
        default=Role.MEMBER.value,
        server_default=Role.MEMBER.value,
        nullable=False,
    )

    recipes = relationship("Recipe", back_populates="author")
    token = relationship("OAuth2Token", back_populates="user", uselist=False)

    @property
    def full_name(self) -> Optional[str]:
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.first_name
        return None

    def is_admin(self):
        return self.role == Role.ADMIN


class OAuth2Token(Base):
    __tablename__ = "oauth2tokens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=40))
    token_type = Column(String(length=40))
    access_token = Column(String(length=200))
    expires_at = Column(TIMESTAMP)
    user_id = Column(
        Integer, ForeignKey("users.id"), index=True, unique=True
    )  # unique=True enforces 1 token per user.

    user = relationship("User", back_populates="token")

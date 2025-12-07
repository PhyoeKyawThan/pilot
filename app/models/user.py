from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import datetime, timezone
import ulid
from passlib.context import CryptContext
from typing import Optional


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


class User(SQLModel, table=True):
    __tablename__ = "user"
    
    user_id: str = Field(
        default_factory=lambda: ulid.new().str,
        primary_key=True
    )

    username: str = Field(nullable=False, min_length=7)
    first_name: str = Field(nullable=False, min_length=6)
    last_name: str = Field(nullable=True)
    email: EmailStr = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)

    created_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_ts: datetime = Field(default=None, nullable=True)
    last_login: Optional[datetime] = Field(default=None, index=True)

    def set_password(self, raw_password: str):
        self.password = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        return pwd_context.verify(raw_password, self.password)

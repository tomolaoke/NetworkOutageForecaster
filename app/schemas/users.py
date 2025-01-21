from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str


class UserCreate(schemas.CreateUpdateDictModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str
    last_name: str

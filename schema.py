from typing import Optional

from pydantic import BaseModel, validator


class CreateUser(BaseModel):
    name: str
    password: str

    @validator("password")
    def secure_password(cls, value):
        if len(value) < 4:
            raise ValueError("Password is too short")
        return value


class UpdateUser(BaseModel):
    name: Optional[str]
    password: Optional[str]

    @validator("password")
    def secure_password(cls, value):
        if len(value) < 4:
            raise ValueError("Password is to short")
        return value


class CreateAd(BaseModel):
    title: str
    description: str
    user_id: int

    @validator("description")
    def tru_description(cls, value):
        if len(value) > 100:
            raise ValueError("Description is too long")
        return value


class UpdateAd(BaseModel):
    title: Optional[str]
    description: Optional[str]
    user_id: Optional[int]

    @validator("description")
    def tru_description(cls, value):
        if len(value) > 100:
            raise ValueError("Description is too long")
        return value

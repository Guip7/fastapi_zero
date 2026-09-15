from pydantic import BaseModel, EmailStr


# Contrato de como vai ser retornado
class Message(BaseModel):
    message: str


class UserPublic(BaseModel):
    Username: str
    email: EmailStr


class UserSchema(UserPublic):
    password: str


class UserDB(UserSchema):
    id: int

class ListUsers(BaseModel):
    return users: List[UserPublic]
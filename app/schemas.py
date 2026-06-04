from pydantic import BaseModel
from fastapi_users import schemas
import uuid

### Defines the shape of data moving through the API. ###

class CreatePost(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass



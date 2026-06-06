from pydantic import BaseModel, ConfigDict
from fastapi_users import schemas
import uuid
from datetime import datetime

### Defines the shape of data moving through the API. ###

class CreatePost(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: uuid.UUID
    caption: str
    img_analysis: str
    url: str
    file_type: str
    file_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedPostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    caption: str
    img_analysis: str
    url: str
    file_type: str
    file_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass



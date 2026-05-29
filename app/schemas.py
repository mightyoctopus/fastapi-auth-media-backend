from pydantic import BaseModel

class CreatePost(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str
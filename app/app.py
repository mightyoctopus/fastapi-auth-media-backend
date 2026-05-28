from fastapi import FastAPI, HTTPException

app = FastAPI()


text_posts = {
    1: {"title": "example1", "content": "placeholder1"},
    2: {"title": "haha2", "content": "placeholder2"}
}

@app.get("/posts")
def get_all_posts():
    return text_posts


@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts.get(id)
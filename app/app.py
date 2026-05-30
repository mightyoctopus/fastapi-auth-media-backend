from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select



# Application startup/shutdown lifecycle manager.
# Runs setup code before the app starts accepting requests.
# The code after 'yield' runs during application shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


# 1. Request with upload file
# 2. Take the file and create a temp file
# 3. Access the database and upload the temp file
# 4. Remove the temp file after all process is complete
@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):

    post = Post(
        caption=caption,
        url="dummy url",
        file_type="photo",
        file_name="dummy name"
    )

    session.add(post)
    await session.commit()
    await session.refresh(post)

    return post


@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    all_posts = result.scalars().all()

    post_data = []

    for post in all_posts:
        post = {
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat(),
        }

        post_data.append(post)

    return {"posts": post_data}











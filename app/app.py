from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from pathlib import Path
from tempfile import NamedTemporaryFile
import shutil
import os
from datetime import datetime




# Application startup/shutdown lifecycle manager.
# Runs setup code before the app starts accepting requests.
# The code after 'yield' runs during application shutdown.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):
    # File extension type/name
    file_suffix = Path(file.filename).suffix

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    # File name concatenated with datetime
    file_name = f"{timestamp}-{str(Path(file.filename))}"

    temp_file_path = None

    try:
        with NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp_file:

            shutil.copyfileobj(file.file, tmp_file)
            temp_file_path = tmp_file.name
            print(f"File temporarily stored at: {temp_file_path}")


        if not temp_file_path or not os.path.exists(temp_file_path):
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )

        response = imagekit.files.upload(
            file=Path(temp_file_path),
            file_name=file_name,
            folder="/uploads",
        )

        post = Post(
            caption=caption,
            url=response.url,
            file_type="video" if file.content_type.startswith("video") else "photo",
            file_name=file_name
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)

        return {
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat()
        }
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


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











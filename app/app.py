import uuid
from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost, PostResponse, FeedPostResponse, UserCreate, UserUpdate, UserRead
from app.db import Post, create_db_and_tables, get_async_session, User
from app.images import imagekit
from app.users import auth_backend, current_active_user, fastapi_users
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.ai import Gpt
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

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


@app.post("/upload", response_model=PostResponse)
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(...),
        user: User = Depends(current_active_user),
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

        llm = Gpt(model="gpt-5-mini")
        img_analysis = llm.call_model(temp_file_path)

        ## How to Transform Images Stored in Imagekit by Parameter modifier
        ## Source: https://imagekit.io/docs/transformations
        response = imagekit.files.upload(
            file=Path(temp_file_path),
            file_name=file_name,
            folder="/uploads",
        )

        post = Post(
            user_id=user.id,
            caption=caption,
            img_analysis=img_analysis,
            url=response.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=file_name
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)

        return post
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed -- {e}"
        )
    finally:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

@app.get("/feed", response_model=list[FeedPostResponse])
async def get_feed(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    all_posts = result.scalars().all()

    return all_posts



@app.delete("/posts/{post_id}")
async def delete_post(
        post_id: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):

    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user.id:
            raise HTTPException(status_code=404, detail="You don't have a permission to delete this post")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": f"Post {post_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error occurred, deleting post {post_id}")







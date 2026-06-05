# FastAPI Image & Video Sharing Backend

A backend API for an image and video sharing application built with FastAPI, FastAPI Users, SQLAlchemy, SQLite, and ImageKit.

## Features

* JWT Authentication
* User Registration
* Email Verification
* Password Reset
* Image Upload
* Video Upload
* Feed Retrieval
* Post Deletion
* User Ownership Validation
* ImageKit Cloud Storage Integration

## Tech Stack

* FastAPI
* FastAPI Users
* SQLAlchemy
* SQLite
* ImageKit
* Pydantic
* Python

## Authentication

The project uses JWT-based authentication powered by FastAPI Users.

Available authentication endpoints:

* Register User
* Login
* Password Reset
* Email Verification
* User Profile Management

## API Endpoints

### Authentication

```http
POST /auth/register
POST /auth/jwt/login
POST /auth/forgot-password
POST /auth/reset-password
POST /auth/request-verify-token
POST /auth/verify
```

### Users

```http
GET /users/me
PATCH /users/me
```

### Posts

#### Upload Post

```http
POST /upload
```

Request:

* File (image/video)
* Caption

Authentication required.

#### Get Feed

```http
GET /feed
```

Returns all uploaded posts ordered by creation date.

Authentication required.

#### Delete Post

```http
DELETE /posts/{post_id}
```

Only the owner of the post can delete it.

Authentication required.

## Database Models

### User

Managed by FastAPI Users.

### Post

Fields:

* id
* user_id
* caption
* url
* file_type
* file_name
* created_at

## Image Storage

Uploaded files are temporarily stored on the server and then uploaded to ImageKit cloud storage.

The temporary file is automatically removed after processing.

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_URL=https://ik.imagekit.io/your_imagekit_id
```

## Installation

```bash
git clone <repo-url>

cd fastapi_backend_image_video_sharing_system

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
uvicorn app.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

for Swagger API documentation.

## Future Improvements

* Pagination
* Like System
* Comment System
* Follow System
* Image Transformations
* Object Storage Migration
* PostgreSQL Deployment
* Role-Based Authorization

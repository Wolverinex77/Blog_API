# Blog API

A production-minded REST API for building and managing a blog platform with
FastAPI, asynchronous SQLAlchemy, PostgreSQL, JWT authentication, and Alembic
database migrations.

## Features

- User registration, login, profiles, and account management
- JWT-based authentication with user and admin authorization
- Post creation, updates, publishing, archiving, and deletion
- Multipart post creation with cover-image uploads
- Categories and reusable tags
- AI-assisted tag suggestions through Gemini
- Flat comments with owner and admin moderation controls
- Public post listing with pagination, filtering, search, and sorting
- Slug generation and uniqueness validation
- Async database access with SQLAlchemy 2
- Versioned schema changes with Alembic

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2 with async sessions
- **Authentication:** JWT and secure password hashing
- **Validation:** Pydantic v2
- **Migrations:** Alembic
- **Image processing:** Pillow
- **AI integration:** Google Gemini

## Project Structure

```text
blog-api/
├── alembic/             # Database migrations
├── app/
│   ├── core/            # Configuration, database, security, exceptions
│   ├── dependencies/    # Authentication and authorization dependencies
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic request and response schemas
│   ├── services/        # Business logic
│   └── uploads/         # Stored cover images
├── tests/               # Test suite
├── alembic.ini
└── requirements.txt
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Wolverinex77/Blog_API.git
cd Blog_API/blog-api
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `blog-api` directory:

```env
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/blog_db
SYNC_DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/blog_db
secret_key=replace-with-a-long-random-secret
access_token_expire_minutes=30
algorithm=HS256
gemini_key=your-gemini-api-key
```

Keep `.env` private. It is excluded from version control.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

## API Documentation

When the server is running, interactive documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Main Endpoints

| Area | Routes |
| --- | --- |
| Authentication | `/auth/register`, `/auth/login` |
| Users | `/users/me`, `/users/admin` |
| Posts | `/posts`, `/posts/{post_id}` |
| Categories | `/categories` |
| Tags | `/tags`, `/tags/posts/{post_id}/suggest-tags` |
| Comments | `/comments`, `/admin/comments/{comment_id}` |

Post listing supports:

```text
GET /posts?page=1&limit=10&search=fastapi&category=backend&tag=python&sort=newest
```

## Development Notes

- Protected endpoints require a bearer token:
  `Authorization: Bearer <access_token>`
- Category creation, category updates/deletion, tag creation, and admin
  moderation require administrator access.
- Post creation and updates use `multipart/form-data` when uploading images.
- Cover images are served from `/uploads/cover_image/...`.

## Running Tests

```bash
pytest
```

## License

This project is intended for learning and development purposes.
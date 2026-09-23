import logging
from pathlib import Path

from app.routers import users, auth, posts, categories, tags, comments, likes
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

project_dir = Path(__file__).resolve().parent.parent
logs_dir = project_dir / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(logs_dir / "app.log", encoding="utf-8"),
    ],
)

app = FastAPI()
uploads_dir = Path(__file__).resolve().parent / "uploads"
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(comments.router)
app.include_router(comments.admin_router)
app.include_router(likes.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
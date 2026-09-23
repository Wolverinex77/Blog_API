from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from enum import Enum
from app.schemas.comment import CommentResponse

class PostCreateStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class PostUpdateStatus(str, Enum):
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PostCreate(BaseModel):
	title: str
	slug: str
	content: str
	excerpt: str | None = None
	status: PostCreateStatus =  PostCreateStatus.DRAFT
	author_id: int | None = None
	category_id: int
	tags: list[str] = Field(default_factory=list)
	cover_image_url: str | None = None


class PostUpdate(BaseModel):
	title: str | None = None
	content: str | None = None
	excerpt: str | None = None
	status: PostUpdateStatus | None = None
	tags: list[str] | None = None


class SelectedTags(BaseModel):
    suggested_tags: list[str]


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    excerpt: str | None = None
    status: str
    author_id: int
    cover_image_url: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostAuthorResponse(BaseModel):
    id: int
    username: str


class PostCategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class PostTagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str | None = None
    cover_image_url: str | None = None
    author: PostAuthorResponse
    likes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostListResponse):
    content: str
    status: str
    author_id: int
    category_id: int
    category: PostCategoryResponse
    tags: list[PostTagResponse]
    comments: list[CommentResponse]
    published_at: datetime | None = None
    updated_at: datetime

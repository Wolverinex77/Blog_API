from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.comment import Comment
    from app.models.like import PostLike
    from app.models.category import Category
    from app.models.tag import Tag
    from app.models.user import User


class PostStatus(str, Enum):
	DRAFT = "draft"
	PUBLISHED = "published"
	ARCHIVED = "archived"


class Post(Base):
	__tablename__ = "posts"

	id: Mapped[int] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column(String, nullable=False)
	slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	excerpt: Mapped[str | None] = mapped_column(String, nullable=True)
	status: Mapped[PostStatus] = mapped_column(
		SQLEnum(PostStatus), nullable=False, default=PostStatus.DRAFT
	)
	# likes_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
	author: Mapped["User"] = relationship("User")
	comments: Mapped[list["Comment"]] = relationship("Comment")
	category_id: Mapped[int] = mapped_column(
		ForeignKey("categories.id"),
		nullable=False,
	)
	category: Mapped["Category"] = relationship("Category")
	likes: Mapped[list["PostLike"]] = relationship("PostLike")
	tags: Mapped[list["Tag"]] = relationship(
		"Tag",
		secondary="post_tags",
	)
	published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
	cover_image_url = mapped_column(String, nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
	)

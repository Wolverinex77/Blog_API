from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tag(Base):
	__tablename__ = "tags"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now()
	)


class PostTag(Base):
	__tablename__ = "post_tags"
	__table_args__ = (
		UniqueConstraint("tag_id", "post_id"),
	)

	id: Mapped[int] = mapped_column(primary_key=True)
	tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)
	post_id: Mapped[int] = mapped_column(
		ForeignKey("posts.id", ondelete="CASCADE"),
		nullable=False,
	)

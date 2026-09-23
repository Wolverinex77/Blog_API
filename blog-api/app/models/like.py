from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PostLike(Base):
	__tablename__ = "post_likes"
	__table_args__ = (
		UniqueConstraint("user_id", "post_id"),
	)

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
	post_id: Mapped[int] = mapped_column(
		ForeignKey("posts.id", ondelete="CASCADE"),
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now()
	)

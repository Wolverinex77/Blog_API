from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Comment(Base):
	__tablename__ = "comments"

	id: Mapped[int] = mapped_column(primary_key=True)
	content: Mapped[str] = mapped_column(Text, nullable=False)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
	post_id: Mapped[int] = mapped_column(
		ForeignKey("posts.id", ondelete="CASCADE"),
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
	)

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    post_id: int
    content: str = Field(min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
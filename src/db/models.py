from sqlalchemy import Integer, DateTime, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid
from datetime import datetime

class BaseModel(DeclarativeBase):
    pass

class PostModel(BaseModel):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(256), primary_key=True)
    views: Mapped[Integer] = mapped_column(Integer(), default=0, nullable=False)

class CommentModel(BaseModel):
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 4"),
        CheckConstraint("LENGTH(comment) >= 1")
    )

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    post: Mapped[str] = mapped_column(ForeignKey("posts.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    comment: Mapped[str] = mapped_column(String(512), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

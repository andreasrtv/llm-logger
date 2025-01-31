from app import db
from datetime import datetime
from flask_login import UserMixin
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.sql import func


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    option_show_completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    option_show_all: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    chats = so.relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Chat(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), nullable=False)
    title: so.Mapped[str] = so.mapped_column(
        sa.String(128), nullable=False, default="New Chat"
    )
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=func.now(), nullable=False
    )

    notes: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    user = so.relationship("User", back_populates="chats")
    messages = so.relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Chat {self.title} (User {self.user_id})>"


class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    chat_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("chat.id"), nullable=False)
    user_message: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    text: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=func.now(), nullable=False
    )

    chat = so.relationship("Chat", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} (Chat {self.chat_id})>"

    def to_dict(self):
        d = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        d["created_at"] = d["created_at"].isoformat().replace("T", " ")
        return d

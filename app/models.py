from app import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.types import CHAR, TypeDecorator
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
import uuid


class UUIDBytes(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            return uuid.UUID(value).bytes
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return str(uuid.UUID(bytes=value))
        return value


chat_tags = db.Table(
    "chat_tags",
    db.Model.metadata,
    sa.Column("chat_id", sa.ForeignKey("chat.id"), primary_key=True),
    sa.Column("tag_id", sa.ForeignKey("tag.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    id: so.Mapped[bytes] = so.mapped_column(
        UUIDBytes, primary_key=True, default=lambda: uuid.uuid4().bytes
    )
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    option_show_completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    option_show_all: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    default_system_prompt: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

    chats = so.relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class Chat(db.Model):
    id: so.Mapped[bytes] = so.mapped_column(
        UUIDBytes, primary_key=True, default=lambda: uuid.uuid4().bytes
    )
    user_id: so.Mapped[bytes] = so.mapped_column(
        sa.ForeignKey("user.id"), nullable=False
    )
    title: so.Mapped[str] = so.mapped_column(
        sa.String(128), nullable=False, default="New Chat"
    )
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=func.now(), nullable=False
    )

    notes: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)
    deleted: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    system_prompt: so.Mapped[str] = so.mapped_column(sa.Text, nullable=True)

    user = so.relationship("User", back_populates="chats")
    messages = so.relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )
    tags: so.Mapped[Optional[list["Tag"]]] = so.relationship(
        "Tag", secondary=chat_tags, back_populates="chats"
    )

    def __repr__(self):
        return f"<Chat {self.title} (User {self.user_id})>"


class Message(db.Model):
    id: so.Mapped[bytes] = so.mapped_column(
        UUIDBytes, primary_key=True, default=lambda: uuid.uuid4().bytes
    )
    chat_id: so.Mapped[bytes] = so.mapped_column(
        sa.ForeignKey("chat.id"), nullable=False
    )
    user_message: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=True)
    text: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, default=func.now(), nullable=False
    )
    parent_id: so.Mapped[Optional[bytes]] = so.mapped_column(
        sa.ForeignKey("message.id"), nullable=True
    )

    chat = so.relationship("Chat", back_populates="messages")

    parent = so.relationship(
        "Message",
        remote_side=[id],
        back_populates="children",
        uselist=False,
        post_update=True,
    )

    children = so.relationship(
        "Message",
        back_populates="parent",
        uselist=True,
        post_update=True,
    )

    def __repr__(self):
        return f'<Message {self.id[:8]} ({self.chat_id[:8]}): "{self.text[:16]}">'

    def to_dict(self):
        d = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        d["created_at"] = d["created_at"].isoformat()

        return d


class Tag(db.Model):
    id: so.Mapped[bytes] = so.mapped_column(
        UUIDBytes, primary_key=True, default=lambda: uuid.uuid4().bytes
    )
    text: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False, unique=True)

    chats = so.relationship("Chat", secondary=chat_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.text}>"

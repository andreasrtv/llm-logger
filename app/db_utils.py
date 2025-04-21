from app import db
from app.models import Chat, Message, Tag, User
from werkzeug.security import generate_password_hash
import uuid


def create_user(username: str, password: str) -> User:
    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash=password_hash)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def get_user_by(username=None, user_id=None) -> User:
    if user_id:
        return User.query.get(user_id)
    elif username:
        return User.query.filter_by(username=username).first()


def edit_user(user_id: str, **kwargs):
    user = User.query.get(user_id)

    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        db.session.commit()


def create_chat(user_id: str) -> str:
    user = get_user_by(user_id=user_id)

    if user.default_system_prompt:
        chat = Chat(user_id=user_id, system_prompt=user.default_system_prompt)
    else:
        chat = Chat(user_id=user_id)

    db.session.add(chat)
    db.session.commit()

    return chat.id


def get_all_chats(deleted=False, completed=False) -> list[Chat]:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed)
        .order_by(db.func.coalesce(Chat.newest_message_at, Chat.created_at).desc())
        .all()
    )


def get_own_chats(user_id: str, deleted=False, completed=False) -> list[Chat]:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed, user_id=user_id)
        .order_by(db.func.coalesce(Chat.newest_message_at, Chat.created_at).desc())
        .all()
    )


def get_newest_chat(deleted=False, completed=False) -> Chat:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed)
        .order_by(db.func.coalesce(Chat.newest_message_at, Chat.created_at).desc())
        .first()
    )


def get_own_newest_chat(user_id: str, deleted=False, completed=False) -> Chat:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed, user_id=user_id)
        .order_by(db.func.coalesce(Chat.newest_message_at, Chat.created_at).desc())
        .first()
    )


def get_chat(chat_id: str) -> Chat:
    return Chat.query.get(chat_id)


def edit_chat(chat_id: str, **kwargs):
    chat = Chat.query.get(chat_id)

    if chat:
        if (
            "system_prompt" in kwargs
            and Message.query.filter_by(chat_id=chat_id).count() != 0
        ):
            raise ValueError(
                "The system prompt can't be changed after the chat has started"
            )

        for key, value in kwargs.items():
            if key == "tag":
                tag = Tag.query.filter_by(text=value).first()
                if tag:
                    chat.tags.append(tag)
                else:
                    raise ValueError(f"Tag '{value}' does not exist")
            else:
                setattr(chat, key, value)

        db.session.commit()


def create_message(
    chat_id: str, text: str, user_message=True, parent_id=None
) -> Message:
    chat = Chat.query.get(chat_id)

    if chat:
        if chat.completed:
            raise ValueError("Can't send message to completed chat")

        message = Message(
            chat_id=chat_id, user_message=user_message, text=text, parent_id=parent_id
        )
        db.session.add(message)
        db.session.commit()

        return message


def get_message(message_id: str) -> Message:
    return Message.query.get(message_id)


def edit_message(message_id: str, text: str):
    message = Message.query.get(message_id)

    if message:
        if message.chat.completed:
            raise ValueError("Can't edit message in completed chat")

        message.text = text
        db.session.commit()


def delete_message(message_id: str):
    message = Message.query.get(message_id)

    if message:
        if message.chat.completed:
            raise ValueError("Can't delete message in completed chat")

        db.session.delete(message)
        db.session.commit()


def get_tags() -> list[Tag]:
    return Tag.query.all()


def create_tag(text: str):
    tag = Tag(text=text)

    db.session.add(tag)
    db.session.commit()


def get_branch_messages(message_id: str) -> list[(Message, list[str])]:
    try:
        selected_id = uuid.UUID(message_id).bytes.hex().upper()
    except ValueError:
        return []

    up_base = db.select(
        Message.id,
        Message.parent_id,
        db.literal(0).label("depth"),
    ).where(db.func.hex(Message.id) == selected_id)

    up_branch = up_base.cte(name="up_branch", recursive=True)

    up_recursive = db.select(
        Message.id,
        Message.parent_id,
        (up_branch.c.depth + 1).label("depth"),
    ).select_from(db.join(Message, up_branch, Message.id == up_branch.c.parent_id))

    up_branch = up_branch.union_all(up_recursive)

    down_base = db.select(
        Message.id,
        Message.parent_id,
        db.literal(0).label("depth"),
    ).where(db.func.hex(Message.id) == selected_id)

    down_branch = down_base.cte(name="down_branch", recursive=True)

    child_subq = (
        db.select(Message.id)
        .where(Message.parent_id == down_branch.c.id)
        .order_by(Message.created_at.asc())
        .limit(1)
        .correlate(down_branch)
        .scalar_subquery()
    )

    down_recursive = db.select(
        Message.id,
        Message.parent_id,
        (down_branch.c.depth + 1).label("depth"),
    ).select_from(db.join(Message, down_branch, Message.id == child_subq))

    down_branch = down_branch.union_all(down_recursive)

    max_depth_cte = db.select(db.func.max(up_branch.c.depth).label("d")).cte(
        "max_depth"
    )

    up_query = db.select(
        up_branch.c.id,
        up_branch.c.parent_id,
        (max_depth_cte.c.d - up_branch.c.depth).label("ordering"),
    ).select_from(db.join(up_branch, max_depth_cte, db.literal(True)))

    down_query = (
        db.select(
            down_branch.c.id,
            down_branch.c.parent_id,
            (max_depth_cte.c.d + down_branch.c.depth).label("ordering"),
        )
        .select_from(db.join(down_branch, max_depth_cte, db.literal(True)))
        .where(down_branch.c.depth > 0)
    )

    final_query = db.union_all(up_query, down_query).order_by(
        db.literal_column("ordering")
    )

    results = db.session.query(Message).from_statement(final_query).all()

    return results

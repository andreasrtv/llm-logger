from app import db
from app.models import Chat, Message, Tag, User
from werkzeug.security import generate_password_hash
import uuid


def commit(obj=None):
    if obj:
        db.session.add(obj)
    db.session.commit()
    return obj


def create_user(username: str, password: str) -> User:
    user = User(username=username, password_hash=generate_password_hash(password))
    return commit(user)


def get_user_by(username: str = None, user_id: str = None) -> User:
    if user_id:
        return User.query.get(user_id)
    if username:
        return User.query.filter_by(username=username).first()
    return None


def edit_user(user_id: str, **attrs) -> User:
    user = get_user_by(user_id=user_id)
    if not user:
        return None
    for key, val in attrs.items():
        setattr(user, key, val)
    db.session.commit()
    return user


def create_chat(user_id: str) -> str:
    user = get_user_by(user_id=user_id)
    prompt = getattr(user, "default_system_prompt", None)
    chat = (
        Chat(user_id=user_id, system_prompt=prompt) if prompt else Chat(user_id=user_id)
    )
    return commit(chat).id


def _base_chats(deleted: bool = False, completed: bool = False, user_id: str = None):
    query = Chat.query.filter_by(deleted=deleted, completed=completed)
    if user_id:
        query = query.filter_by(user_id=user_id)
    return query.order_by(
        db.func.coalesce(Chat.newest_message_at, Chat.created_at).desc()
    )


def get_chats(
    user_id: str = None, deleted: bool = False, completed: bool = False
) -> list[Chat]:
    if user_id:
        return _base_chats(deleted, completed, user_id).all()

    return _base_chats(deleted, completed).all()


def get_newest_chat(
    user_id: str = None, deleted: bool = False, completed: bool = False
) -> Chat:
    if user_id:
        return _base_chats(deleted, completed, user_id).first()
    return _base_chats(deleted, completed).first()


def get_chat(chat_id: str) -> Chat:
    return Chat.query.get(chat_id)


def edit_chat(chat_id: str, **kwargs):
    chat = get_chat(chat_id)
    if not chat:
        return None

    if "system_prompt" in kwargs and chat.messages:
        raise ValueError(
            "The system prompt can't be changed after the chat has started"
        )

    for k, v in kwargs.items():
        if k == "tag":
            tag = Tag.query.filter_by(text=v).first()
            if not tag:
                raise ValueError(f"Tag '{v}' does not exist")
            chat.tags.append(tag)
        else:
            setattr(chat, k, v)

    db.session.commit()
    return chat


def create_message(
    chat_id: str, text: str, user_message: bool = True, parent_id: str = None
) -> Message:
    chat = get_chat(chat_id)
    if not chat:
        return None

    if chat.completed:
        raise ValueError("Can't send message to completed chat")

    msg = Message(
        chat_id=chat_id, user_message=user_message, text=text, parent_id=parent_id
    )
    return commit(msg)


def get_message(message_id: str) -> Message:
    return Message.query.get(message_id)


def edit_message(message_id: str, text: str):
    msg = get_message(message_id)
    if not msg:
        return None

    if msg.chat.completed:
        raise ValueError("Can't edit message in completed chat")

    msg.text = text
    db.session.commit()
    return msg


def delete_message(message_id: str):
    msg = get_message(message_id)
    if not msg:
        return None

    if msg.chat.completed:
        raise ValueError("Can't delete message in completed chat")

    db.session.delete(msg)
    db.session.commit()


def get_tags() -> list[Tag]:
    return Tag.query.all()


def create_tag(text: str):
    tag = Tag(text=text)
    return commit(tag)


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


def parse_bool_values(data):
    return {
        key: (value.lower() == "true" if value.lower() in ["true", "false"] else value)
        for key, value in data.items()
    }


def get_chats_for_user(user, newest=False):
    if newest:
        return (
            get_newest_chat(completed=user.option_show_completed)
            if user.option_show_all
            else get_newest_chat(user_id=user.id, completed=user.option_show_completed)
        )

    return (
        get_chats(completed=user.option_show_completed)
        if user.option_show_all
        else get_chats(user_id=user.id, completed=user.option_show_completed)
    )

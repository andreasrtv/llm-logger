from app import db
from app.models import Chat, Message, User, Tag
from werkzeug.security import generate_password_hash


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
        .order_by(Chat.created_at.desc())
        .all()
    )


def get_own_chats(user_id: str, deleted=False, completed=False) -> list[Chat]:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed, user_id=user_id)
        .order_by(Chat.created_at.desc())
        .all()
    )


def get_newest_chat(deleted=False, completed=False) -> Chat:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed)
        .order_by(Chat.created_at.desc())
        .first()
    )


def get_own_newest_chat(user_id: str, deleted=False, completed=False) -> Chat:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed, user_id=user_id)
        .order_by(Chat.created_at.desc())
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


def create_message(chat_id: str, text: str, user_message=True) -> Message:
    chat = Chat.query.get(chat_id)
    if chat:
        if chat.completed:
            raise ValueError("Can't send message to completed chat")

        message = Message(chat_id=chat_id, user_message=user_message, text=text)
        db.session.add(message)
        db.session.commit()

        return message


def edit_message(message_id: str, text: str):
    message = Message.query.get(message_id)

    if message:
        chat = Chat.query.get(message.chat_id)
        if chat.completed:
            raise ValueError("Can't edit message in completed chat")

        message.text = text
        db.session.commit()


def get_tags() -> list[Tag]:
    return Tag.query.all()


def create_tag(text: str):
    tag = Tag(text=text)

    db.session.add(tag)
    db.session.commit()

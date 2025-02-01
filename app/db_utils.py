from app import db
from app.models import Chat, Message, User
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


def create_chat(user_id: int) -> int:
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


def get_own_chats(user_id: int, deleted=False, completed=False) -> list[Chat]:
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


def get_own_newest_chat(user_id: int, deleted=False, completed=False) -> Chat:
    return (
        Chat.query.filter_by(deleted=deleted, completed=completed, user_id=user_id)
        .order_by(Chat.created_at.desc())
        .first()
    )


def get_messages(chat_id: int) -> list[Message]:
    return Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()


def create_message(chat_id: int, text: str, user_message=True) -> Message:
    chat = Chat.query.get(chat_id)
    if chat:
        if chat.completed:
            raise ValueError("Can't send message to completed chat")

        message = Message(chat_id=chat_id, user_message=user_message, text=text)
        db.session.add(message)
        db.session.commit()

        return message


def edit_chat(chat_id: int, **kwargs):
    chat = Chat.query.get(chat_id)

    if chat:
        for key, value in kwargs.items():
            if value == "True":
                value = True
            elif value == "False":
                value = False
            setattr(chat, key, value)
        db.session.commit()


def edit_user(user_id: int, **kwargs):
    user = User.query.get(user_id)

    if user:
        for key, value in kwargs.items():
            if value == "True":
                value = True
            elif value == "False":
                value = False
            setattr(user, key, value)
        db.session.commit()


def edit_message(message_id: int, text: str):
    message = Message.query.get(message_id)

    if message:
        chat = Chat.query.get(message.chat_id)
        if chat.completed:
            raise ValueError("Can't edit message in completed chat")

        message.text = text
        db.session.commit()

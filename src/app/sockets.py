from app import db_utils, llm, login_manager, socketio
from flask_login import current_user
from flask_socketio import close_room, emit, join_room, rooms
import sqlalchemy


@login_manager.user_loader
def load_user(user_id):
    return db_utils.get_user_by(user_id=user_id)


@socketio.on("connect")
def handle_connect():
    if not current_user.is_authenticated:
        return False


@socketio.on("join")
def on_join(chat_id):
    if not current_user.is_authenticated:
        return False

    for room in rooms():
        close_room(room)

    join_room(str(chat_id))


@socketio.on("leave")
def on_leave(chat_id):
    if not current_user.is_authenticated:
        return False

    close_room(str(chat_id))


@socketio.on("send_message")
def handle_message(data):
    if not current_user.is_authenticated:
        return False

    chat_id = data["chat_id"]
    text = data["text"]
    parent_id = data.get("parent_id", None)

    try:
        user_message = db_utils.create_message(chat_id, text, parent_id=parent_id)
        llm_message = db_utils.create_message(
            user_message.chat_id,
            "Reasoning...",
            user_message=False,
            parent_id=user_message.id,
        )
    except ValueError:
        return False

    if not user_message or not llm_message:
        return False

    ws_message = user_message.to_dict()
    ws_message["stream"] = False

    emit(
        "new_message",
        ws_message,
        room=str(chat_id),
    )

    ws_message = llm_message.to_dict()
    ws_message["stream"] = True

    emit(
        "new_message",
        ws_message,
        room=str(llm_message.chat_id),
    )

    send_message_stream(llm_message)


@socketio.on("reprompt_message")
def handle_reprompt_message(data):
    if not current_user.is_authenticated:
        return False

    chat_id = data["chat_id"]
    message_id = data["message_id"]

    message = db_utils.get_message(message_id)
    if not message or message.user_message or message.chat.completed:
        return False

    db_utils.edit_message(message_id, "Reasoning...")
    emit(
        "new_message_stream",
        {"text": "Reasoning...", "message_id": message_id},
        room=str(chat_id),
    )

    send_message_stream(message)


@socketio.on("delete_message")
def handle_delete_message(data):
    if not current_user.is_authenticated:
        return False

    chat_id = data["chat_id"]
    message_id = data["message_id"]

    try:
        db_utils.delete_message(message_id)
    except ValueError:
        return False

    emit(
        "delete_message",
        {"message_id": message_id},
        room=str(chat_id),
    )


def send_message_stream(message):
    message_id = message.id
    chat_id = message.chat_id

    try:
        for chunk in llm.respond(message):
            emit(
                "new_message_stream",
                {"text": chunk, "message_id": message.id},
                room=str(message.chat_id),
            )

        emit(
            "new_message_done",
            {"message_id": message.id},
            room=str(message.chat_id),
        )
    except Exception as e:
        emit(
            "error",
            {
                "error": str(e),
                "message_id": message_id,
            },
            room=str(chat_id),
        )

        return

from app import db_utils, login_manager, socketio, llm
from flask_login import current_user
from flask_socketio import close_room, emit, join_room, rooms


@login_manager.user_loader
def load_user(user_id):
    return db_utils.get_user_by(user_id=int(user_id))


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

    message = db_utils.create_message(chat_id, text)

    if not message:
        return False

    emit(
        "new_message",
        message.to_dict(),
        room=str(chat_id),
    )

    llm_response = llm.query(chat_id)

    emit(
        "new_message",
        llm_response.to_dict(),
        room=str(chat_id),
    )

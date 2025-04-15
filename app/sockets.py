from app import db_utils, llm, login_manager, socketio
from flask_login import current_user
from flask_socketio import close_room, emit, join_room, rooms


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
    except ValueError:
        return False

    if not user_message:
        return False

    user_message = user_message.to_dict()
    user_message["stream"] = False

    emit(
        "new_message",
        user_message,
        room=str(chat_id),
    )

    try:
        llm_stream = llm.query(user_message)

        llm_message = next(llm_stream).to_dict()
        message_id = llm_message["id"]
        llm_message["stream"] = True

        emit(
            "new_message",
            llm_message,
            room=str(chat_id),
        )

        for chunk in llm_stream:
            emit(
                "new_message_stream",
                {"text": chunk, "message_id": message_id},
                room=str(chat_id),
            )

        emit(
            "new_message_done",
            {"message_id": message_id},
            room=str(chat_id),
        )
    except Exception as e:
        if "message_id" not in locals() or not message_id:
            message_id = None

        emit(
            "error",
            {
                "error": str(e),
                "message_id": message_id,
            },
            room=str(chat_id),
        )

        return

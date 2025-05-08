from app import db_utils, llm, login_manager, socketio
from flask_login import current_user
from flask_socketio import close_room, emit, join_room, rooms
import functools


@login_manager.user_loader
def load_user(user_id):
    return db_utils.get_user_by(user_id=user_id)


def require_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return False
        return f(*args, **kwargs)

    return wrapper


@socketio.on("connect")
@require_auth
def handle_connect():
    return True


@socketio.on("join")
@require_auth
def on_join(chat_id):
    for r in rooms():
        close_room(r)
    join_room(str(chat_id))


@socketio.on("leave")
@require_auth
def on_leave(chat_id):
    close_room(str(chat_id))


@socketio.on("send_message")
@require_auth
def handle_message(data):
    chat_id = data.get("chat_id")
    text = data.get("text")
    parent_id = data.get("parent_id")

    try:
        user_msg = db_utils.create_message(chat_id, text, parent_id=parent_id)
        llm_msg = db_utils.create_message(
            chat_id,
            "Reasoning...",
            user_message=False,
            parent_id=user_msg.id,
        )
    except ValueError:
        return False

    if not user_msg or not llm_msg:
        return False

    msg = user_msg.to_dict()
    msg["stream"] = False
    emit("new_message", msg, room=str(chat_id))

    msg = llm_msg.to_dict()
    msg["stream"] = True
    emit("new_message", msg, room=str(chat_id))

    _stream_response(llm_msg)


@socketio.on("reprompt_message")
@require_auth
def handle_reprompt(data):
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    msg = db_utils.get_message(message_id)

    if not msg or msg.user_message or msg.chat.completed:
        return False

    db_utils.edit_message(message_id, "Reasoning...")
    emit(
        "new_message_stream",
        {"text": "Reasoning...", "message_id": message_id},
        room=str(chat_id),
    )

    _stream_response(msg)


@socketio.on("delete_message")
@require_auth
def handle_delete(data):
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    try:
        db_utils.delete_message(message_id)
    except ValueError:
        return False

    emit(
        "delete_message",
        {"message_id": message_id},
        room=str(chat_id),
    )


def _stream_response(message):
    mid = message.id
    cid = str(message.chat_id)

    try:
        for chunk in llm.respond(message):
            emit("new_message_stream", {"text": chunk, "message_id": mid}, room=cid)

        emit("new_message_done", {"message_id": mid}, room=cid)
    except Exception as e:
        emit("error", {"error": str(e), "message_id": mid}, room=cid)

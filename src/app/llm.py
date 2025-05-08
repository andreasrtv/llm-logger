from app import Config, db_utils
from time import sleep

if not Config.MOCK_LLM_RESPONSES:
    from app import openai_client


def mock_query():
    sleep(0.5)
    words = Config.FAKE_RESPONSE.split()

    for x, _ in enumerate(words):
        yield " ".join(words[: x + 1])
        sleep(0.08)


def build_conversation(message):
    chat = db_utils.get_chat(message.chat_id)
    msgs = db_utils.get_branch_messages(message.parent.id)
    conv = []

    if chat.system_prompt:
        conv.append({"role": "developer", "content": chat.system_prompt})

    conv.extend(
        {"role": "user" if m.user_message else "assistant", "content": m.text}
        for m in msgs
        if m.text
    )

    return conv


def query(message):
    conversation = build_conversation(message)

    try:
        stream = openai_client.chat.completions.create(
            messages=conversation, model=Config.AI_MODEL, stream=True
        )
    except Exception:
        db_utils.delete_message(message.id)
        raise

    response = ""
    try:
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                response += delta
                yield response
    except Exception:
        if isinstance(response, str):
            db_utils.edit_message(message.id, response)
        raise


def respond(message):
    if Config.MOCK_LLM_RESPONSES:
        stream = mock_query()
    else:
        stream = query(message)

    response = ""

    for x, response in enumerate(stream):
        yield response
        if x % 20 == 0:
            db_utils.edit_message(message.id, response)

    db_utils.edit_message(message.id, response)

from app import Config, db_utils
from time import sleep

if not Config.MOCK_LLM_RESPONSES:
    from app import openai_client


def mock_query():
    sleep(0.5)
    message = Config.FAKE_RESPONSE.split(" ")

    for x in range(len(message)):
        yield " ".join(message[: x + 1])
        sleep(0.08)


def query(message):
    chat = db_utils.get_chat(message.chat_id)
    messages = db_utils.get_branch_messages(message.parent.id)
    conversation = []

    if chat.system_prompt:
        conversation.append({"role": "developer", "content": chat.system_prompt})

    conversation += [
        {"role": "user" if m.user_message else "assistant", "content": m.text}
        for m in messages
        if m.text != ""
    ]

    try:
        stream = openai_client.chat.completions.create(
            messages=conversation, model=Config.AI_MODEL, stream=True
        )
    except Exception as e:
        db_utils.delete_message(message.id)
        raise e

    response = ""

    try:
        for chunk in stream:
            if len(chunk.choices) == 0:
                continue

            chunked_response = chunk.choices[0].delta.content
            if chunked_response:
                response += chunked_response

                yield response
    except Exception as e:
        if response and type(response) == str:
            db_utils.edit_message(message.id, response)

        raise e


def respond(message):
    if Config.MOCK_LLM_RESPONSES:
        stream = mock_query()
    else:
        stream = query(message)

    for x, response in enumerate(stream):
        yield response

        if x % 20 == 0:
            db_utils.edit_message(message.id, response)

    db_utils.edit_message(message.id, response)

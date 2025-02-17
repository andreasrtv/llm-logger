from app import Config, db_utils, openai_client
from time import sleep


def fake_stream():
    class dotdict(dict):
        __getattr__ = dict.get
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

    message = open("fake_response.txt").read().split(" ")
    message = [m + " " for m in message]

    for m in message:
        yield dotdict({"choices": [dotdict({"delta": dotdict({"content": m})})]})
        sleep(0.01)


def query(chat_id):
    if Config.USE_FAKE_LLM:
        stream = fake_stream()
    else:
        conversation = []

        chat = db_utils.get_chat(chat_id)
        messages = chat.messages

        if chat.system_prompt:
            conversation.append({"role": "system", "content": chat.system_prompt})

        conversation += [
            {"role": "user" if m.user_message else "assistant", "content": m.text}
            for m in messages
        ]

        stream = openai_client.chat.completions.create(
            messages=conversation, model="gpt-4o-2024-08-06", stream=True
        )

    chunk = next(stream)

    response = chunk.choices[0].delta.content
    new_message = db_utils.create_message(chat_id, response, user_message=False)

    yield new_message

    try:
        save_interval = 20
        i = 0

        for chunk in stream:
            chunked_response = chunk.choices[0].delta.content
            if chunked_response:
                response += chunked_response

                yield chunked_response

                i += 1
                if i % save_interval == 0:
                    db_utils.edit_message(new_message.id, response)

    except Exception:
        if response and type(response) == str:
            db_utils.edit_message(new_message.id, response)

    db_utils.edit_message(new_message.id, response)

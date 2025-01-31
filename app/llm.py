from app import db_utils, openai_client


# TODO: Add an editable system prompt to each chat (based on a default system prompt). Add the chat's system prompt to the conversation before sending it to the LLM.
def query(chat_id):
    messages = db_utils.get_messages(chat_id)

    conversation = [
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
        for chunk in stream:
            chunked_response = chunk.choices[0].delta.content
            if chunked_response:
                response += chunked_response

                yield chunked_response
    except Exception:
        if response and type(response) == str:
            db_utils.edit_message(new_message.id, response)

    db_utils.edit_message(new_message.id, response)

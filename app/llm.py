from app import db_utils, openai_client


# TODO: Add an editable system prompt to each chat (based on a default system prompt). Add the chat's system prompt to the conversation before sending it to the LLM.
def query(chat_id):
    messages = db_utils.get_messages(chat_id)

    conversation = [
        {"role": "user" if m.user_message else "assistant", "content": m.text}
        for m in messages
    ]

    chat_completion = openai_client.chat.completions.create(
        messages=conversation,
        model="gpt-4o-2024-08-06",
    )

    response = chat_completion.choices[0].message.content

    return db_utils.create_message(chat_id, response, user_message=False)

from app import Config, db_utils
from time import sleep
from pydantic import BaseModel, Field
from typing import List
import json

if not Config.MOCK_LLM_RESPONSES:
    from app import openai_client


def fake_stream():
    sleep(0.5)
    message = Config.FAKE_RESPONSE.split(" ")

    for x in range(len(message)):
        yield " ".join(message[: x + 1])
        sleep(0.08)


class ResponseModel(BaseModel):
    reasoning: str = Field(
        ...,
        description="Describe and reason about the user's message and their needs.",
    )
    actions: List[str] = Field(
        ...,
        description="3 alternative responses to the user's message. Each response should describe 1 action that the user can peform. Answer with as much detail as necessary, you do not have to limit yourself.",
    )


def query(user_message):
    message = db_utils.create_message(
        user_message["chat_id"],
        "Reasoning...\n",
        user_message=False,
        parent_id=user_message["id"],
    )

    yield message

    if Config.MOCK_LLM_RESPONSES:
        stream = fake_stream()

        for m in stream:
            yield m

        db_utils.edit_message(message.id, m)
    else:
        conversation = []

        chat = db_utils.get_chat(user_message["chat_id"])
        messages = db_utils.get_branch_messages(user_message["id"])

        if chat.system_prompt:
            conversation.append({"role": "developer", "content": chat.system_prompt})

        conversation += [
            {"role": "user" if m.user_message else "assistant", "content": m.text}
            for m in messages
        ]

        with openai_client.beta.chat.completions.stream(
            messages=conversation,
            model=Config.AI_MODEL,
            response_format=ResponseModel,
        ) as stream:
            for event in stream:
                if event.type == "content.delta" and event.parsed is not None:
                    content = json.dumps(event.parsed)
                    if content == "{}":
                        continue
                    db_utils.edit_message(message.id, content)
                    yield content

        final = stream.get_final_completion()

        final_content = final.choices[0].message.parsed.model_dump_json()
        db_utils.edit_message(message.id, final_content)

        yield final_content

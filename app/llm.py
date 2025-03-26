from app import Config, db_utils, openai_client
from time import sleep
from pydantic import BaseModel, Field
from typing import List
import json


def fake_stream():
    sleep(0.5)
    message = open("fake_response.txt").read().split(" ")

    for x in range(len(message)):
        yield " ".join(message[: x + 1])
        sleep(0.08)


class ResponseModel(BaseModel):
    reasoning: str = Field(
        ...,
        description="Describe the logic and reasoning behind the recommendation.",
    )
    actionable_steps: List[str] = Field(
        ...,
        description="A list of exactly 3 steps or practical actions to address the issue.",
    )


def query(user_message):
    message = db_utils.create_message(
        user_message["chat_id"],
        "Reasoning...\n",
        user_message=False,
        parent_id=user_message["id"],
    )

    yield message

    if Config.USE_FAKE_LLM:
        stream = fake_stream()

        for m in stream:
            yield m

        db_utils.edit_message(message.id, m)
    else:
        conversation = []

        chat = db_utils.get_chat(user_message["chat_id"])
        messages = [m[0] for m in db_utils.get_branch_messages(user_message["id"])]

        if chat.system_prompt:
            conversation.append({"role": "developer", "content": chat.system_prompt})

        conversation += [
            {"role": "user" if m.user_message else "assistant", "content": m.text}
            for m in messages
        ]

        with openai_client.beta.chat.completions.stream(
            messages=conversation,
            model="o3-mini",
            response_format=ResponseModel,
        ) as stream:
            for event in stream:
                if event.type == "content.delta" and event.parsed is not None:
                    content = json.dumps(event.parsed)
                    db_utils.edit_message(message.id, content)
                    yield content

        final = stream.get_final_completion()

        final_content = final.choices[0].message.parsed.model_dump_json()
        db_utils.edit_message(message.id, final_content)

        yield final_content

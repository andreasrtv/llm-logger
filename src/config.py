import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    MOCK_LLM_RESPONSES = os.getenv("MOCK_LLM_RESPONSES", "false").lower() == "true"

    if MOCK_LLM_RESPONSES:
        if not os.path.isfile(os.path.join(BASE_DIR, "fake_response.txt")):
            raise ValueError("No fake response file found.")

        FAKE_RESPONSE = open(os.path.join(BASE_DIR, "fake_response.txt")).read()
    else:
        AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        if AZURE_OPENAI_API_KEY:
            AI_MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
        elif OPENAI_API_KEY:
            AI_MODEL = os.getenv("OPENAI_MODEL")
        else:
            raise ValueError(
                "No API key provided. Either set MOCK_LLM_RESPONSES=true or provide an API key."
            )

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.getenv('DB_PATH', os.path.join(BASE_DIR, 'database.db'))}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    USE_FAKE_LLM = os.getenv("USE_FAKE_LLM", "False").lower() == "true"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

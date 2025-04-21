from gevent import monkey

monkey.patch_all()

from config import Config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

moment = Moment(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

socketio = SocketIO(app, async_mode="gevent")

if not app.config["MOCK_LLM_RESPONSES"]:
    if app.config["AZURE_OPENAI_API_KEY"]:
        from openai import AzureOpenAI

        openai_client = AzureOpenAI(
            api_version="2024-12-01-preview",
            api_key=app.config["AZURE_OPENAI_API_KEY"],
            azure_endpoint=app.config["AZURE_ENDPOINT"],
        )
    elif app.config["OPENAI_API_KEY"]:
        from openai import OpenAI

        openai_client = OpenAI(api_key=app.config["OPENAI_API_KEY"])
    else:
        raise ValueError(
            "No API key provided. Either set MOCK_LLM_RESPONSES=true or provide an API key."
        )

from app import db_utils, models, routes, sockets, llm

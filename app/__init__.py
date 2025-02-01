from gevent import monkey

monkey.patch_all()

from config import Config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"

socketio = SocketIO(app, async_mode="gevent")

openai_client = OpenAI(
    api_key=app.config["OPENAI_API_KEY"]
)

from app import db_utils, models, routes, sockets, llm

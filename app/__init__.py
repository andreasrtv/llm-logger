from config import Config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import openai

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"

socketio = SocketIO(app)

openai_client = OpenAI()

from app import db_utils, models, routes, sockets, llm

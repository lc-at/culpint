import eventlet
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_pyfile('config.py')

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
db = SQLAlchemy(app)

from .api import bp as api_bp  # noqa
from .views import *  # noqa: E402,F401,F403

app.register_blueprint(api_bp)

from .socketio_events import *  # noqa

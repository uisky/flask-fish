from flask.config import Config
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect


db = SQLAlchemy()

csrf = CsrfProtect()


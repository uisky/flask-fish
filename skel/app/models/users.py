import hashlib
import string
import random

from flask import current_app

from {{ name }}.core import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)

    name = db.Column(db.String(255), nullable=False, default='')
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255))

    def __repr__(self):
        return '<User %d:%s>' % (0 if self.id is None else self.id, self.name)

    @staticmethod
    def hash_password(data):
        return hashlib.md5((data + current_app.config['SECRET_KEY']).encode()).hexdigest()

    @property
    def is_active(self):
        return bool(self.roles & 1)

    @property
    def is_authenticated(self):
        return bool(self.roles & 1)

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    def get_id(self):
        return str(self.id)


class PasswordRecoveryToken(db.Model):
    __tablename__ = 'password_recovery_tokens'

    @staticmethod
    def gentoken():
        return ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(64)])

    token = db.Column(db.String(255), nullable=False, primary_key=True, default=gentoken)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False, primary_key=True)
    created = db.Column(db.DateTime(timezone=True), server_default=db.text('now()'), nullable=False)
    cnt_errors = db.Column(db.Integer, server_default=db.text('0'), default=0, nullable=False)

import time
from hashlib import sha512

from . import app, db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    @classmethod
    def create_user(cls, username, password):
        password_hash = sha512(password.encode()).hexdigest()
        user = cls()
        user.username = username
        user.password = password_hash
        db.session.add(user)
        db.session.commit()

    @classmethod
    def authenticate(cls, username, password):
        password_hash = sha512(password.encode()).hexdigest()
        user = cls.query.filter_by(username=username,
                                   password=password_hash).first()
        if user:
            return True
        elif not cls.query.filter_by(username=username).first() \
                and username == app.config['SU_USERNAME']:
            su = cls()
            su.username = username
            su.password = password_hash
            db.session.add(su)
            db.session.commit()
            return True
        return False

    @classmethod
    def change_password(cls, username, new_password):
        user = cls.query.filter_by(username=username).first()
        password_hash = sha512(new_password.encode()).hexdigest()
        user.password = password_hash
        db.session.commit()

    @staticmethod
    def generate_token(username):
        expiration_ts = str(round((time.time() + 3600)))
        pt_token = ''.join((username, expiration_ts, app.config['SECRET_KEY']))
        return ':'.join((expiration_ts, sha512(pt_token.encode()).hexdigest()))

    @staticmethod
    def validate_token(username, token):
        expiration_ts, token_hash = token.split(':')
        pt_token = ''.join((username, expiration_ts, app.config['SECRET_KEY']))
        hashed = sha512(pt_token.encode()).hexdigest()
        return hashed == token_hash and time.time() < int(expiration_ts)


db.create_all()
db = db

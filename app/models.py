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


db.create_all()
db = db

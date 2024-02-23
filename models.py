"""SQLAlchemy models for Capstone 1."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()



class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True,)

    username = db.Column(db.String(20), nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    profile_image_url = db.Column( db.Text, default="/static/images/alt_profile_img.jpg",)

    reviews = db.relationship('Review', backref='users')

    ratings = db.relationship('Rating', backref='users')


    @classmethod
    def signup(cls, username, password, profile_image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            profile_image_url=profile_image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Rating(db.Model):
    """Ratings of game by user"""

    __tablename__ = 'ratings'

    user_id = db.Column( db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True,)

    game_id = db.Column( db.Integer, primary_key=True,)

    rating = db.Column(db.Integer, nullable=False)

class ListsTable(db.Model):
    """Lists of games by user"""

    __tablename__ = 'lists'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)

    list_name = db.Column(db.String(80), nullable=False)



class ListEntriesTable(db.Model):
    """Connection of a Game <-> List"""

    __tablename__ = 'list_games'

    id = db.Column(db.Integer, primary_key=True,)
    
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete="cascade"), nullable=False)

    game_id = db.Column(db.Integer, nullable=False)

    
class Review(db.Model):
    """Reviews of game by user"""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True,)
    
    user_id = db.Column( db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True,)

    game_id = db.Column( db.Integer, primary_key=True,)

    text = db.Column(db.Text, nullable=False)

    timestamp = db.Column( db.DateTime, nullable=False, default=datetime.utcnow(),)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
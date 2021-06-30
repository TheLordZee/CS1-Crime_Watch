from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Follows(db.Model):
    """M2M table of followers and followed users"""

    __tablename__ = 'followers'

    user_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )
    
    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

class Favorites(db.Model):
    """M2M table connecting users to their favorite jokes"""
    __tablename__ = 'favorites'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

    joke_id = db.Column(
        db.Integer,
        db.ForeignKey('jokes.id', ondelete="cascade"),
        primary_key=True
    )

class Ratings(db.Model):
    """M2M table for ratings"""

    __tablename__ = 'ratings'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True
    )

    joke_id = db.Column(
        db.Integer,
        db.ForeignKey('jokes.id', ondelete="cascade"),
        primary_key=True
    )

    rating = db.Column(
        db.Boolean,
        nullable=False
    )

class Comment(db.Model):
    """Comment model"""

    __tablename__ = 'comments'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    joke_id = db.Column(
        db.Integer,
        db.ForeignKey('jokes.id', ondelete="cascade")
    )

    comment = db.Column(
        db.text,
        nullable=False
    )

class Report(db.Model):
    """Report model"""

    __tablename__ = 'reports'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    reporter_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False
    )

    joke_id = db.Column(
        db.Integer,
        db.ForeignKey('jokes.id', ondelete="cascade"),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=False
    )

class User(db.Model):
    """User Model"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    jokes = db.relationship('Joke')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_followed_id == id)
    )

    favorites = db.relationship(
        'Joke',
        secondary="favorites"
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Checks if user is followed by 'other_user'"""

        found_user_list = [user for user in self.followers if user == other_user]

        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Checks if user is following 'other_user'"""

        found_user_list = [user for user in self.following if user == other_user]

        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, img_url):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            img_url=img_url
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Finds user with `username` and checks if `password` hash matches the stored password. """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class JokeTags(db.model):
    """M2M table between tags and jokes"""

    __tablename__ = 'joke_tags'

    tag_id = db.Column(
        db.Integer,
        db.ForeignKey('tags.id', ondelete="cascade"),
        primary_key=True
    )

    joke_id = db.Column(
        db.Integer,
        db.ForeignKey('jokes.id', ondelete="cascade"),
        primary_key=True
    )


class Joke(db.Model):
    """Jokes model"""

    __tablename__ = 'jokes'
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False
    )

    setup = db.Column(
        db.Text,
        nullable=False
    )

    body = db.Column(
        db.Text,
        nullable=False
    )

    user = db.relationship('User')

class Tag(db.Model):
    """Tag model"""

    __tablename__ = 'tags'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.text,
        nullable=False
    )

def connect_db(app):
    """Connects database to Flask App"""

    db.app = app
    db.init_app(app)
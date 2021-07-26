from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class Follows(db.Model):
    """M2M table of followers and followed users"""

    __tablename__ = 'follows'

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
        db.Integer,
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

    comment_text = db.Column(
        db.Text,
        nullable=False
    )

class Report(db.Model):
    """Report model"""

    __tablename__ = 'reports'
    
    reporter_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        nullable=False,
        primary_key=True
    )

    joke_id = db.Column(
        db.Integer,
        db.ForeignKey('jokes.id', ondelete="cascade"),
        nullable=False,
        primary_key=True
    )

    reported_at = db.Column(
        db.DateTime,
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=False
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
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False
    )

    nsfw = db.Column(
        db.Boolean,
        default=False
    )

    def serialize(self):
        joke_json = {
            'id': self.id,
            'user_id': self.user_id,
            'setup': self.setup,
            'body': self.body,
            'created_at': self.get_date(),
            'is_nsfw': self.nsfw,
            'username': self.user.username
        }

        return joke_json

    def get_date(self):
        return self.created_at.strftime("%b %d %Y at %I:%M%p")

    user = db.relationship('User')

    rating = db.relationship('Ratings')

    def calculate_rating(self):
        total_rating = 0
        for r in self.rating:
            total_rating = total_rating + r.rating

        return total_rating

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

    show_nsfw = db.Column(
        db.Boolean,
        default=False
    )

    email_verified = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False
    )

    blocked_jokes = db.Column(
        db.ARRAY(db.Integer),
        default=[]
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
        "Joke",
        secondary="favorites"
    )

    ratings = db.relationship("Ratings")

    def serialize(self):
        user_json = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_admin': self.is_admin,
            'show_nsfw': self.show_nsfw,
            'created_at': self.created_at
        }

        return user_json

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
    def signup(cls, username, email, password, image_url, show_nsfw, created_at):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            show_nsfw=show_nsfw,
            created_at=created_at
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


class JokeTags(db.Model):
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

class Tag(db.Model):
    """Tag model"""

    __tablename__ = 'tags'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

class Id(db.Model):
    """Stores the id for the last joke retrieved from the joke api to make sure that the same joke doesn't get called multiple times. No other data should be stored here."""

    id = db.Column( 
        db.Integer,
        primary_key=True
    )

    last_joke_id = db.Column(
        db.Integer
    )

def connect_db(app):
    """Connects database to Flask App"""

    db.app = app
    db.init_app(app)
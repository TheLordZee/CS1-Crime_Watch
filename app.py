import os
from flask.globals import session
from flask.helpers import flash
from forms import *
from flask import Flask, json, render_template, request, jsonify, redirect, g
from models import *
from sqlalchemy.exc import *
from sqlalchemy.sql import func
from flask_debugtoolbar import DebugToolbarExtension
import requests
from func import *


app = Flask(__name__)

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///jokebook_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

BASE_URL = 'https://v2.jokeapi.dev/joke/'

@app.before_request
def add_user_to_g():

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

####################################################################################################
#Homepage

@app.route("/")
def homepage():
    """Show homepage."""
    get_random_joke()
    top_joke=''

    jokes = db.session.query(
        Joke, 
        func.sum(Ratings.rating)
    ).join(Ratings).group_by(Joke.id).order_by(func.sum(Ratings.rating).desc()).all()

    for j in jokes:
        if datetime.now() - j[0].created_at <= timedelta(days=7):
            top_joke = j[0]
            return render_template('home.html', top_joke=top_joke, in_week=True)
    
    top_joke=jokes[0][0]
    return render_template('home.html', top_joke=top_joke, in_week=False)
####################################################################################################
#User signup/login/logout    

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handles user sign up. Creates a new user if valid else it shows the form again"""

    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or "/static/images/default-pic.png",
                created_at=datetime.now()
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')

        do_login(user)

        return redirect('/')

    return render_template('users/signup.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("User was logged out. We're sorry to see you go.", 'success')
    return redirect('/')


@app.route('/login', methods=['GET','POST'])
def login():
    """Handles user login"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}", "success")
            return redirect("/")
        
        flash("Invalid username or password", 'danger')
    
    return render_template("users/login.html", form=form)

####################################################################################################
#Joke Routes
@app.route('/quick-joke')
def show_quick_joke_page():
    return render_template('jokes/quick-joke.html')

@app.route('/jokes/add', methods=["GET","POST"])
def add_joke():
    """Adds a Joke. Displays form and, if valid,adds joke to database"""

    if not g.user:
        flash("Access denied, please signup or login", "danger")
        return redirect("/")

    form = JokeForm()

    if form.validate_on_submit():
        setup = form.setup.data
        body = form.body.data

        new_joke = Joke(user_id=g.user.id, setup=setup, body=body, created_at=datetime.now())

        db.session.add(new_joke)
        db.session.commit()

        return redirect(f"/")

    return render_template('jokes/new.html', form=form)

    
@app.route('/jokes/<int:id>/edit', methods=["GET","POST"])
def edit_joke(id):
    joke = Joke.query.get_or_404(id)
    form = JokeForm()

    if form.validate_on_submit():
        joke.setup = form.setup.data
        joke.body = form.body.data
        db.session.commit()
        return redirect('/')
    
    form.body.data = joke.body
    return render_template('jokes/edit.html', form=form, joke=joke)

@app.route('/jokes/page/<int:page>')
def put_jokes_on_page(page):
    offset = (page - 1) * 10
    end = False
    if g.user:
        if g.user.show_nsfw == False:
            jokes = Joke.query.filter(Joke.nsfw == False).order_by(Joke.created_at.desc()).limit(10).offset(offset).all()
        else:
            jokes = Joke.query.order_by(Joke.created_at.desc()).limit(10).offset(offset).all()
    else:
        jokes = Joke.query.filter(Joke.nsfw == False).order_by(Joke.created_at.desc()).limit(10).offset(offset).all()
    
    if len(jokes) < 10:
        end = True

    return render_template('jokes/jokes-page.html', jokes=jokes, page=page, end=end)                

"""User routes"""
@app.route('/users/<int:user_id>/profile')
def show_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    num_jokes = len(user.jokes)
    return render_template('users/profile.html', user=user, num_jokes=num_jokes)

"""api routes"""
@app.route('/api/jokes/<int:joke_id>/rate', methods=['POST'])
def update_joke_rating(joke_id):
    if g.user:
        rating = request.json['rating']
        if rating == 1 or rating == -1:
            try:
                rate_joke(g.user.id, joke_id, rating)
                json_res = {
                    "error": False,
                    "message":"rating added"
                }
            
            except IntegrityError or InvalidRequestError:
                db.session.rollback()
                joke_rating = Ratings.query.get((g.user.id, joke_id))
                if rating != joke_rating.rating:
                    joke_rating.rating = rating
                    db.session.commit()
                    json_res = {
                        "error":False,
                        "message":"rating updated"
                    }
                else:
                    db.session.delete(joke_rating)
                    db.session.commit()
                    json_res = {
                        "error":False,
                        "message": "rating removed"
                    }
        else:
            print(request.json)
            json_res = {
                "error":True,
                "message": "invalid value"
            }                       
        return jsonify(json_res)

@app.route('/api/jokes/random-joke')
def send_random_joke():
    joke = get_random_joke()
    if joke == False:
        json = {
            'joke': None
        }
    else:
        json = { 
           'joke': joke.serialize()
        }
    return jsonify(json)

@app.route('/api/get_curr_user')
def get_curr_user():
    if g.user:
        json = {
            'logged_in': True,
            'curr_user': g.user.serialize()
        }
    else:
        json = {
            'logged_in': False
        }

    return jsonify(json)

@app.route('/api/check_for_curr_user')
def check_for_curr_user():
    if g.user:
        json = {
            'logged_in_user': True,
            'user_id': g.user.id
        }      
    else:
        json = {
            'logged_in_user': False
        }

    return jsonify(json)
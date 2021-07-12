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

    top_joke=''

    if len(Joke.query.order_by(Joke.created_at.desc()).all()) > 0:
        jokes = db.session.query(
            Joke, 
            func.sum(Ratings.rating)
        ).join(Ratings).group_by(Joke.id).order_by(func.sum(Ratings.rating)).all()
    
        for j in jokes:
            if datetime.now() - j[0].created_at <= timedelta(days=7):
                print(j[0])
                top_joke = j[0]
                return render_template('home.html', top_joke=top_joke, in_week=True)
       
        top_joke=jokes[0][0]
        in_week=False
                

    else:
        if g.user:
            if g.user.show_nsfw == True:
                res = requests.get(BASE_URL + 'Any')
            else:        
                res = requests.get(BASE_URL + 'Any?safe-mode')
        else:
            res = requests.get(BASE_URL + 'Any?safe-mode')

        joke_json = res.json()
        if joke_json['type'] == 'twopart':
            top_joke = Joke(
                user_id=1, 
                setup=joke_json['setup'],
                body=joke_json['delivery'],
                created_at=random_date()
            )
            db.session.add(top_joke)
            db.session.commit()
            rate_joke(1, top_joke, 1)
    
    if datetime.now() - top_joke.created_at <= timedelta(days=7):
        in_week = True
    else:
        in_week = False
    return render_template('home.html', top_joke=top_joke, in_week=in_week)
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
                image_url=form.image_url.data or "/static/images/default-pic.png"
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
    if g.user:
        if g.user.show_nsfw == False:
            jokes = Joke.query.filter(Joke.nsfw == False).order_by(Joke.created_at.desc()).limit(10).offset(offset).all()
        else:
            jokes = Joke.query.order_by(Joke.created_at.desc()).limit(10).offset(offset).all()
    else:
        jokes = Joke.query.filter(Joke.nsfw == False).order_by(Joke.created_at.desc()).limit(10).offset(offset).all()

    if len(jokes) < 10:
        """Makes sure """
        prev_joke = Id.query.get(1)
        prev_joke_id = prev_joke.last_joke_id

        while len(jokes) < 10:
            req = requests.get(BASE_URL + f'Any?idRange={prev_joke_id + 1}-{prev_joke_id + 10}&amount=10')
            prev_joke_id = prev_joke_id + 10
            jokes_json = req.json()
            if jokes_json['error'] == True and len(jokes) > 0:
                return render_template('joke-page.hmtl', jokes=jokes,   end=True)
            elif jokes_json['error'] == True and len(jokes) == 0:
                return render_template('404.html')

            for j in jokes_json['jokes']:
                if j['type'] == 'twopart':
                    new_joke = Joke(
                        user_id=1,
                        setup=j['setup'],
                        body=j['delivery'],
                        created_at=random_date(),
                        nsfw=not j['safe']
                    )
                    db.session.add(new_joke)
                    db.session.commit()
                    if g.user:
                        if g.user.show_nsfw == False and new_joke.nsfw ==   True:
                            """does nothing when user doesn't want nsfw and the joke is nsfw"""
                            print('joke does not go in')
                        else:
                            jokes.append(new_joke)
                    else:
                        if new_joke.nsfw == False:
                            """Not logged in users don't get to see nsfw    jokes"""
                            jokes.append(new_joke)

        prev_joke.last_joke_id = prev_joke_id
        db.session.commit()

    return render_template('jokes/jokes-page.html', jokes=jokes, page=page, end=False)                


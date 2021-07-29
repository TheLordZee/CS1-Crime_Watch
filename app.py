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
from datetime import datetime, timedelta


app = Flask(__name__)

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '*&H-H*-87hup978hnuh98j')
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

    if g.user:
        jokes = db.session.query(
            Joke, 
            func.sum(Ratings.rating)
        ).join(Ratings).group_by(Joke.id).filter(Joke.id not in g.user.blocked_jokes).order_by(func.sum(Ratings.rating).desc()).all()
    else:
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
                show_nsfw=form.show_nsfw.data,
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


@app.route('/jokes/following/page/<int:page>')
def show_followed_users_jokes(page):
    offset = (page - 1) * 10
    end = False
    if g.user:
        if g.user.show_nsfw == True:
            fol_jokes = (db.session
                    .query(Joke, Follows)
                    .filter(Follows.user_following_id == g.user.id, Joke.user_id == Follows.user_followed_id)
                    .order_by(Joke.created_at.desc())
                    .limit(10)
                    .offset(offset)
                    .all())
        else:
            fol_jokes = (db.session
                    .query(Joke, Follows)
                    .filter(Follows.user_following_id == g.user.id, Joke.user_id == Follows.user_followed_id, Joke.nsfw == False)
                    .order_by(Joke.created_at.desc())
                    .limit(10)
                    .offset(offset)
                    .all()
            )
        
        jokes = []
        for j in fol_jokes:
            jokes.append(j[0])

        if len(jokes) < 10:
            end = True

        return render_template('jokes/followed.html', jokes=jokes, page=page, end=end)

"""User routes"""
@app.route('/users/<int:user_id>/profile')
def show_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    num_jokes = len(user.jokes)
    return render_template('users/profile.html', user=user, num_jokes=num_jokes)

@app.route('/users/<int:u_id>/favorites')
def show_fav_jokes(u_id):
    user = User.query.get_or_404(u_id)
    return render_template('jokes/fav-jokes.html', user=user)

@app.route('/users/<int:u_id>/settings', methods=["GET", "POST"])
def edit_user_settings(u_id):
    if u_id == g.user.id:
        form = EditUserForm()
        if form.validate_on_submit():
            g.user.username = form.username.data
            g.user.email = form.email.data 
            g.user.image_url = form.image_url.data 
            g.user.show_nsfw = form.show_nsfw.data
            db.session.commit()
            return redirect(f'/users/{g.user.id}/profile')

        form.username.data = g.user.username
        form.email.data = g.user.email
        form.image_url.data = g.user.image_url
        form.show_nsfw.data = g.user.show_nsfw
        return render_template('users/settings.html', form=form, u_id=u_id)
    
    return redirect('/')

"""report route"""

@app.route('/reports')
def show_reports():
    if g.user:
        if g.user.is_admin:
            reports = db.session.query(
                Joke, 
                func.count(Report.joke_id)
            ).join(Report).group_by(Joke.id).order_by(func.count(Report.joke_id).desc()).all()
            return render_template('reports.html', reports=reports)
    
    return redirect('/')

"""api routes"""

@app.route('/api/jokes/rate', methods=['POST'])
def update_joke_rating():
    if g.user:
        joke_id = request.json['joke_id']
        rating = request.json['rating']
        if rating == 1 or rating == -1:
            if  Ratings.query.get((g.user.id, joke_id)):
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
                rate_joke(g.user.id, joke_id, rating)
                json_res = {
                    "error": False,
                    "message":"rating added"
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

@app.route('/api/jokes/favorite', methods=["POST"])
def favorite_joke():
    if g.user:
        joke_id = request.json['joke_id']
        if Favorites.query.get((g.user.id, joke_id)):
            fav = Favorites.query.get((g.user.id, joke_id))
            db.session.delete(fav)
            db.session.commit()
            json = {
                'error': False,
                'message': 'Favorite removed'
            }
        else:
            favorite = Favorites(user_id=g.user.id, joke_id=joke_id)
            db.session.add(favorite)
            db.session.commit()
            json = {
                'error': False,
                'message': 'Joke favorited'
            }
        return jsonify(json)

@app.route('/api/jokes/delete', methods=["DELETE"])
def delete_joke():
    if g.user:
        joke_id = request.json['joke_id']
        joke = Joke.query.get(joke_id)
        if joke.user == g.user or g.user.is_admin:
            for report in joke.reports:
                db.session.delete(report)
                db.session.commit()
            for rating in joke.rating:
                db.session.delete(rating)
                db.session.commit()

            db.session.delete(joke)
            db.session.commit()
            json = {
                'error': False,
                'message':'joke deleted'
            }
        else:
            json = {
                'error': True,
                'message': "you aren't allowed to delete this joke"
            }
    else:
        json = {
            'error': True,
            'message': "you aren't allowed to delete this joke"
        }

    return jsonify(json)

@app.route('/api/users/follow', methods=['POST'])
def follow_user():
    if g.user:
        user_id = request.json['u_id']
        user = User.query.get(user_id)
        if g.user.is_following(user):
            follow = Follows.query.get((user_id, g.user.id))
            db.session.delete(follow)
            db.session.commit()
            json = {
                'error': False,
                'type': 'unfollow',
                'message': f'{g.user.username} unfollowed {user.username}'
            }
        else:
            g.user.following.append(user)
            db.session.commit()
            json = {
                'error': False,
                'type': 'follow',
                'message': f'{g.user.username} followed {user.username}'
            }

        return jsonify(json)

@app.route('/api/report', methods=["POST"])
def report_joke():
    if g.user:
        joke_id = request.json['joke_id']
        reason = request.json['reason']
        if not Report.query.get((g.user.id, joke_id)):
            report = Report(
                reporter_id=g.user.id,
                joke_id=joke_id,
                reported_at=datetime.now(),
                reason=reason
            )
            
            blocked_jokes = g.user.blocked_jokes.copy()
            blocked_jokes.append(joke_id)
            g.user.blocked_jokes = blocked_jokes

            db.session.add(report)
            db.session.commit()

            json = {
                "error": False,
                "message": "joke reported"
            }
        else:
            json = {
                "error": True,
                "message": "you can't report the same joke more than once"
            }
        print(g.user.blocked_jokes)
        return jsonify(json)

@app.route('/api/report/cancel', methods=["DELETE"])
def cancel_report():
    if g.user:
        if g.user.is_admin:
            joke_id = request.json['joke_id']
            reports = db.session.query(Report).filter(Report.joke_id == joke_id).all()
            for report in reports:
                db.session.delete(report)

            db.session.commit()
            json = {
                'error': False,
                'message': 'report canceled'
            }
        else:
            json = {
                'error': True,
                'message': 'only admins can cancel reports'
            }
    else:
            json = {
                'error': True,
                'message': 'only admins can cancel reports'
            }

    return jsonify(json)
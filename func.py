from flask.globals import session
from datetime import datetime, timedelta
from models import *
import random
from apscheduler.schedulers.background import BackgroundScheduler
import requests
BASE_URL = 'https://v2.jokeapi.dev/joke/'
from flask import g


sched = BackgroundScheduler(daemon=True)
sched.add_job(lambda : get_api_jokes(), 'interval', days=1)
sched.start()

def get_api_jokes():
    print('jokes retrieved')
    prev_joke = Id.query.get(1)
    prev_joke_id = prev_joke.last_joke_id 
    req = requests.get(BASE_URL + f'Any?idRange={prev_joke_id + 1}-{prev_joke_id + 10}&amount=10')
    prev_joke_id = prev_joke_id + 10
    jokes_json = req.json()
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
            
        elif j['type'] == 'single':
            new_joke = Joke(
                user_id=1,
                setup=j['joke'],
                created_at=random_date(),
                nsfw=not j['safe']
            )
            db.session.add(new_joke)
            db.session.commit()
        
        print(new_joke)
        rate_joke(1, new_joke.id, 1)
    prev_joke.last_joke_id = prev_joke_id
    db.session.commit()


def random_date():
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)

    return(random_date)
    
def rate_joke(user_id, joke_id, rating):
    
    if rating == 1 or rating == -1:
        joke_rating = Ratings(
            user_id=user_id,
            joke_id=joke_id,
            rating=rating
        )
        db.session.add(joke_rating)
        db.session.commit()

def get_random_joke():
    ids = []
    user_rated_ids = []
    if 'prev_joke_id'  not in session:
        session['prev_joke_id'] = -1
    if g.user:
        for r in g.user.ratings:
            user_rated_ids.append(r.joke_id)
        print(user_rated_ids)
        if g.user.show_nsfw == False:
            joke_ids = db.session.query(Joke.id).filter(Joke.nsfw == False, Joke.id != session['prev_joke_id']).all()
        else:
            joke_ids = db.session.query(Joke.id).filter(Joke.id != session['prev_joke_id']).all()
    else:
        joke_ids = db.session.query(Joke.id).filter(Joke.nsfw == False, Joke.id != session['prev_joke_id']).all()
    
    for i in joke_ids:
        if i[0] not in user_rated_ids:
            ids.append(i[0])
    if len(ids) == 0:
        return False
    ran_id = random.choice(ids)

    session['prev_joke_id'] = ran_id
    ran_joke = Joke.query.get(ran_id)
    return ran_joke
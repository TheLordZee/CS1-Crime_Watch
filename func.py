from datetime import datetime, timedelta
from models import Joke, Ratings, db
import random

def random_date():
    start_date = datetime.fromisoformat('2021-01-01')
    end_date = datetime.fromisoformat('2021-07-01')

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)

    return(random_date)

def within_week(date):
    
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day

    currdate = '{}-{}-{}'.format(year, month, day)
    currdate = datetime.strptime(currdate, '%Y-%m-%d')

    joke_date = '{date.year}-{date.month}-{date.day}'

    print(joke_date)

    days = currdate - timedelta(int(joke_date[-2:]))
    days = str(days)
    print(days)

    if int(days[8:11]) <= 7:
        return True
    else:
        return False
    
def rate_joke(u_id, joke, rating):
    
    if rating == 1 or rating == -1:
        joke_rating = Ratings(
            user_id=u_id,
            joke_id=joke.id,
            rating=rating
        )
        db.session.add(joke_rating)
        db.session.commit()
    
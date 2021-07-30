from app import db
from models import *
from datetime import datetime
from func import *

db.drop_all()
db.create_all()

defualt_user = User(
    email='thezanderco@gmail.com',
    username='JokeBot',
    password='$2b$12$ZJ2ei5Ej4j/A8detgOqVd.4i8V9BwfgcZO7zPeZ3PcUK8s6t75ieW',
    is_admin=True,
    image_url='/static/images/jokebot-pic.png',
    show_nsfw=True,
    email_verified=True,
    created_at=datetime.now()
)

admin_user = User(
    email='thelordzee@gmail.com', 
    username='LordZee', 
    password='$2b$12$q/OnZOtisFGWp9Biho/Zs.efiddagXYF0WYlZAKicLeI9OLhxbRbm', 
    is_admin=True, 
    image_url='/static/images/admin-pic.png', 
    show_nsfw=True, 
    email_verified=True,
    created_at=datetime.now()
)

start_id = Id(
    last_joke_id=0
)

db.session.add_all([defualt_user, admin_user, start_id])
db.session.commit()

get_api_jokes()
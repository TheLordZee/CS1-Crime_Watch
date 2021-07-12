from app import db
from models import *
from datetime import datetime

db.drop_all()
db.create_all()

defualt_user = User(
    email='thezanderco@gmail.com', 
    username='LordZee', 
    password='$2b$12$q/OnZOtisFGWp9Biho/Zs.efiddagXYF0WYlZAKicLeI9OLhxbRbm', 
    is_admin=True, 
    image_url='static/images/admin-pic.png', 
    show_nsfw=True, 
    email_verified=True,
    created_at=datetime.now()
)

start_id = Id(
    last_joke_id=0
)

db.session.add_all([defualt_user, start_id])
db.session.commit()
from flask_sqlalchemy import SQLAlchemy
from __main__ import app


db = SQLAlchemy(app)

class UserInfo(db.Model):
    ###User model### 

    __tablename__ = "userInfo"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username 
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User {}>'.format(self.username)

# class Blogs(db.Model):
#     pass 

# class User_blog(db.Model):
#     pass






db.create_all()

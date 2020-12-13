from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
from datetime import timedelta
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy import ForeignKey
from werkzeug.exceptions import default_exceptions
from datetime import datetime
from sqlalchemy.orm import relationship


app = Flask(__name__)
#set the timeline the session can last
app.permanent_session_lifetime = timedelta(days=5)
SECRET_KEY = 'secret key'

#Configure Flask by providing the PostgreSQL URI 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Asebomu12@localhost/Mozes721'
#needs to be placed after app is created


###Model declaration
db = SQLAlchemy(app)
class Users(db.Model):
    ###User model### 
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_blog = db.relationship('Posts', backref='list', lazy=True)

    def __init__(self, username, email, password):
        self.username = username 
        self.email = email
        self.password = password
        

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    post_time = db.Column(db.DateTime, index=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.String(500), unique=False, nullable=False)
    parent_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self,post_time, title, content, parent_id):
        self.post_time = post_time
        self.title = title 
        self.content = content
        self.parent_id = parent_id
    def __repr__(self):
     return f"Post('{self.title}', '{self.post_time}')"

# class Blogs(db.Model):
#     pass 

# db.create_all()



#Routes
@app.route('/', methods= ['post', 'get'])
def index():
    #set the session as permanent with the given lifetime
    session.permanent = True
    if "username" not in session:
        #status(disabled) so that logout and your posts are only accesible ones logged in
        return render_template('index.html', status="disabled")
    else:
        username = session["username"]
        user_id = session
        flash("You are already logged in as %s" % username)
        return render_template("index.html")

#register route
@app.route('/register', methods= ["POST", "GET"])
def register():
    if "username" in session:
            username = session["username"]
            flash("You are already logged in as %s" % username)
            return render_template("register.html")
    else:
        if request.method == "POST":
            email = request.form.get("email")
            username = request.form.get("username")
            password = request.form.get("password")
            #encrypt password 
            hashed = sha256_crypt.encrypt(password)
            #if empty flash a message
            if email == '' or username == '' or password == '':
                flash("Please enter all input fields!")
                return redirect(url_for("register", status="disabled"))
            #check if user already in database
            if db.session.query(Users.id).filter_by(email = email).scalar() or db.session.query(Users.id).filter_by(username = username).scalar() is not None:
                flash("The email or username already is being used please choose a different one or login if your an existing user")
                return redirect(url_for("register", status="disabled"))
            #if not add the new user and redirect
            register_user = Users(email = email, username = username, password = hashed)
            db.session.add(register_user)
            db.session.commit()
            #create a session while user logged in
            session["username"] = username
            flash("You have logged in as %s" % username)
            return redirect(url_for('members', usr=username))
        return render_template('register.html', status="disabled")


#login route
@app.route('/login', methods= ["POST", "GET"])
def login():
    #check if user already in session(logged in)
    if "username" in session:
        username = session["username"]
        flash("You are already logged in as %s" % username)
        return render_template("login.html")
    else:
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            hashed = sha256_crypt.encrypt(password)
            if username == '' or password == '':
                flash("Please enter all input fields!")
                return redirect(url_for("login", status="disabled"))
            #check if user already exists in database
            if db.session.query(Users.id).filter_by(username = username).scalar():
                #check if password match specific user
                if db.session.query(Users.id).filter_by(password = hashed):
                    db.session.query(Users.id)
                    session["username"] = username
                    flash("You have logged in as %s" % username)
                    return redirect(url_for('members'))
                flash("Password is incorect please try again")
                return redirect(url_for("login", status="disabled"))
            flash("Username is incorect please try again")
            return redirect(url_for("login", status="disabled"))
        return render_template('login.html', status="disabled")




#user_form route
@app.route('/user', methods= ["POST", "GET"])
def members():
    #only if user is in session otherwise redirect
    if "username" in session:
        #get the user in current session
        username = session["username"]
        if request.method == "POST":
            title = request.form.get("title")
            content = request.form.get("content")
            if title == '' or content == '':
                flash("Please enter all input fields!")
                return redirect(url_for("members"))
            #retrive the user ID from Users class model 
            user_id = db.session.query(Users.id).filter_by(username = username).scalar()
            #add to posts database the coresponding values and assign to the right userID
            post = Posts(post_time=datetime.now(), title=title, content=content, parent_id=user_id)      
            db.session.add(post)
            db.session.commit()
            flash("Your post was sucesfully submited")
            return redirect(url_for('members'))
        return render_template('members.html')
    else:
        return redirect(url_for("index", status="disabled"))



@app.route('/logout', methods=["GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
        flash("You have been logged out!")
        resp = app.make_response(render_template('login.html', status="disabled"))
        resp.set_cookie('token', expires=0)
        return resp 
    else:
        flash("You have been already logged out")
        return redirect(url_for("login"))
        

#detects changes and updates on relode
if __name__ == '__main__':
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(debug=True)

from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
from datetime import timedelta
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, update
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField ,SubmitField, validators
from sqlalchemy import desc
from py_paginator import Paginator

app = Flask(__name__)
#set the timeline the session can last
app.permanent_session_lifetime = timedelta(days=5)

SECRET_KEY = 'secret key'

#Configure Flask by providing the PostgreSQL URI 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Password@localhost/Database'
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


class PostForm(FlaskForm):
    post_time = datetime.today().replace(microsecond=0)
    title = StringField('title', [validators.InputRequired()])
    content = TextAreaField('content', [validators.InputRequired()])
    submit = SubmitField('Submit')


#Routes
@app.route('/')
def index():
    #all posts
    page = request.args.get('page', 1, type=int)
    all_posts = db.session.query(Posts.post_time, Posts.title, Posts.content, Users.username).join(Posts)\
        .order_by(Posts.post_time.desc()).paginate(page=page, per_page=3)
    
    session.permanent = True    
    if "username" not in session:
        #status(disabled) so that logout and your posts are only accesible ones logged in
        return render_template('index.html', status="disabled", posts=all_posts)
    else:
        username = session["username"]
        flash("You are already logged in as %s" % username)
            
        return render_template("index.html", posts=all_posts)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        username = request.form.get("username")
        if db.session.query(Users.id).filter_by(username = username).scalar():
            user_id = db.session.query(Users.id).filter_by(username = username).scalar()
            user_posts = db.session.query(Posts).filter_by(parent_id=user_id)\
                .order_by(Posts.post_time.desc())
            return render_template('search.html', posts=user_posts, usr=username)
        else:
            flash("There is no post by  %s" % username)
            return redirect(url_for('index'))
    
        
    
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
            flash("Username or password is incorect please try again or register!")
            return redirect(url_for("login", status="disabled"))
        return render_template('login.html', status="disabled")




#user_form route
@app.route('/user/', methods= ["POST", "GET"])
def members():
    #only if user is in session otherwise redirect
    if "username" in session:
        #get the user in current session
        username = session["username"]
        #retrive the user ID from Users class model and as well all he posts from the user
        page = request.args.get('page', 1, type=int)
        
        user_id = db.session.query(Users.id).filter_by(username = username).scalar()
        user_posts = db.session.query(Posts).filter_by(parent_id=user_id)\
            .order_by(Posts.post_time.desc()).paginate(page=page, per_page=3)
        #initiate declarative form class
        form = PostForm()
        #get the values from the input fields
        title = form['title'].data
        content = form['content'].data

        if request.method == "POST":
            #add to posts database the coresponding values and assign to the right userID
            post = Posts(post_time=form.post_time ,title=title, content=content, parent_id=user_id)
            db.session.add(post)
            db.session.commit()
            flash("Your post was sucesfully submited")
            return redirect(url_for('members', form=form, posts=user_posts))
        return render_template('members.html', form=form, posts=user_posts)
    else:
        return redirect(url_for("index", status="disabled"))
#Edit Post
@app.route('/edit_post/<string:id>', methods= ["POST", "GET"])
def edit_post(id):
    #get the post values by id
    post = db.session.query(Posts).filter_by(id = id).first()
    #fetch the id of the post
    post_id = db.session.query(Posts.id).filter_by(id = id).first()
    #populate PostForm with the existing fields
    form = PostForm(obj=post)
    if request.method == "POST":
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        flash("The post has been updatet")
        return redirect(url_for('members'))
    return render_template('edit_post.html',id=post_id, form=form)

#Delete Post
@app.route('/delete_post/<string:id>', methods=['POST'])
def delete_post(id):
    if "username" in session:
        #create cursor
        db.session.query(Posts).filter_by(id = id).delete()
        db.session.commit()

        flash("Post deleted")
        return redirect(url_for('members'))
    else:
        flash("You have to login as a user of the post!")
        return redirect(url_for("login", status="disabled"))



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

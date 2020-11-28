from flask import Flask, render_template, request, session, redirect, url_for, flash
import hashlib
from datetime import timedelta
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
#set the timeline the session can last
app.permanent_session_lifetime = timedelta(days=5)
SECRET_KEY = 'secret key'

#Configure Flask by providing the PostgreSQL URI 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/database'
#needs to be placed after app is created


from models import db, UserInfo
#migrate the app and the models 
migrate = Migrate(app, db)
#assign to flask_script manager the app
manager = Manager(app)
#make final migration
manager.add_command('db', MigrateCommand)




@app.route('/', methods= ['post', 'get'])
def index():
    #set the session as permanent with the given lifetime
    session.permanent = True
    return render_template('index.html')

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
            #if empty flash a message
            if email == '' or username == '' or password == '':
                flash("Please enter all input fields!")
                return redirect(url_for("register"))
            #check if user already in database
            if db.session.query(UserInfo.id).filter_by(email = email).scalar() or db.session.query(UserInfo.id).filter_by(username = username).scalar() is not None:
                flash("The email or username already is being used please choose a different one or login if your an existing user")
                return redirect(url_for("register"))
            #if not add the new user and redirect
            register_user = UserInfo(email = email, username = username, password = password)
            db.session.add(register_user)
            db.session.commit()
            #create a session while user logged in
            session["username"] = username
            flash("You have logged in as %s" % username)
            return redirect(url_for('members', usr=username))
        return render_template('register.html')


#login route
@app.route('/login', methods= ['post', 'get'])
def login():
    #check if user already in session(logged in)
    if "username" in session:
        username = session["username"]
        flash("You are already logged in as %s" % username)
        return render_template("login.html")
    else:
        if request.method == "POST":
            print("Hello im posting!")
            username = request.form.get("username")
            password = request.form.get("password")
            if username == '' or password == '':
                flash("Please enter all input fields!")
                return redirect(url_for("login"))
            #check if user already exists in database
            if db.session.query(UserInfo.id).filter_by(username = username).scalar():
                #check if password match specific user
                if db.session.query(UserInfo.id).filter_by(password = password).scalar():
                    session["username"] = username
                    flash("You have logged in as %s" % username)
                    return redirect(url_for('members'))
                flash("Password is incorect please try again")
                return redirect(url_for("login"))
            flash("Username is incorect please try again")
            return redirect(url_for("login"))
        return render_template('login.html')




#user_form route
@app.route('/user', methods= ['post', 'get'])
def members():
    #only if user is in session otherwise redirect
    if "username" in session:
        username = session["username"]
        flash("You have logged in as %s" % username)
        return render_template('members.html')
    else:
        return redirect(url_for("index"))



@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("You have been logged out!", "info")
    return redirect(url_for("index"))
        

#detects changes and updates on relode
if __name__ == '__main__':
    app.config['SECRET_KEY'] = SECRET_KEY
    app.run(debug=True)

from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
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
    if "username" not in session:
        #status(disabled) so that logout and your posts are only accesible ones logged in
        return render_template('index.html', status="disabled")

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
            if db.session.query(UserInfo.id).filter_by(email = email).scalar() or db.session.query(UserInfo.id).filter_by(username = username).scalar() is not None:
                flash("The email or username already is being used please choose a different one or login if your an existing user")
                return redirect(url_for("register", status="disabled"))
            #if not add the new user and redirect
            register_user = UserInfo(email = email, username = username, password = hashed)
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
            if db.session.query(UserInfo.id).filter_by(username = username).scalar():
                #check if password match specific user
                if db.session.query(UserInfo.id).filter_by(password = hashed):
                    db.session.query(UserInfo.id)
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

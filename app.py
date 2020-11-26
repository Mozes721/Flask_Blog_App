from flask import Flask 
from flask import render_template #render the html pages
from flask import request #get user input from form
import hashlib
from flask_sqlalchemy import SQLAlchemy
import psycopg2
#to manage models in seperate file
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)

#Configure Flask by providing the PostgreSQL URI 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Password@localhost/Database'
#needs to be placed after app is created
from models import db
#migrate the app and the models 
migrate = Migrate(app, db)
#assign to flask_script manager the app
manager = Manager(app)
#make final migration
manager.add_command('db', MigrateCommand)




@app.route('/', methods= ['post', 'get'])
def index():
    message = ''
    return render_template('index.html')

#register route
@app.route('/register', methods= ['post', 'get'])
def register():
    return render_template('register.html')

#login route
@app.route('/login', methods= ['post', 'get'])
def login():
    return render_template('login.html')

#logout route
@app.route('/logout', methods= ['post', 'get'])
def logout():
    return render_template('logout.html')

#detects changes and updates on relode
if __name__ == '__main__':
    app.run(debug=True)
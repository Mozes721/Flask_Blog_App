from flask import Flask 
from flask import render_template #render the html pages
from flask import request #get user input from form
import hashlib
import psycopg2

app = Flask(__name__)

#render the base template
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
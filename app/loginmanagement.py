from flask import Flask, render_template, request, redirect, url_for, session, escape
from flaskext.mysql import MySQL
import flask_login
import re

#mySQL loading
mysql = MySQL()
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mysql.init_app(app)

#our site login management
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


def getUsers():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()

# user connection to database
class User(flask_login.UserMixin, flask_login.AnonymousUserMixin):
    def __init__(self):
        app = Flask(__name__)
        self.mysql = MySQL()
        app.config.from_pyfile('config.cfg')
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()

    # returns user_id of user who was just created
    def create_user(self, first_name, last_name, email, password):
        #user_id must be unique
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Users (first_name, last_name, email, password) VALUES ('{0}', '{1}', '{2}', '{3}')".format(first_name,last_name, email, password))
        self.conn.commit()
        return cursor.lastrowid

    def set_twitter_username(self, user_id, twitter_username):
        cursor = self.conn.cursor()
        query = "UPDATE Users SET twitter_username = '{0}' WHERE user_id = {1}".format(twitter_username, user_id)
        cursor.execute(query)
        self.conn.commit()
        
    def set_twitter_id(self, user_id, twitter_id):
        cursor = self.conn.cursor()
        query = "UPDATE Users SET twitter_user_id = '{0}' WHERE user_id = {1}".format(twitter_id, user_id)
        cursor.execute(query)
        self.conn.commit()

    def get_name(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT first_name FROM Users WHERE user_id = '{0}'".format(user_id))
        response = cursor.fetchone()[0]
        return response

    # returns twitter_username, twitter_api_key
    def get_twitter_info(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT twitter_username FROM Users WHERE user_id = '{0}'".format(user_id))
        response = cursor.fetchone()
        return response[0]
    
@login_manager.user_loader
def user_loader(email):
    users = getUsers()
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUsers()
    email = request.form.get('email')
    if not(email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    return user 

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    if cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email)):
        return cursor.fetchone()[0]
    else:
        return None

def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM Users WHERE email = '{0}'".format(email)):
        return False
    else:
        return True
    
def login():
    if request.method == 'GET':
        return render_template("login.html")
    #The request method is POST (page is recieving data)
    email = request.form['email']
    if email == "":
        return render_template("login.html", message="Please try again!")
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        print("!!!")
        print(data)
        if data == ():
            return render_template("login.html", message="Please try again!")
        pwd = str(data[0][0])
        if request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            return render_template('index.html', name=user.get_name(getUserIdFromEmail(flask_login.current_user.id)),logged_in=flask_login.current_user.is_authenticated)
 
    #information did not match
    return render_template('login.html', message="Please try again!")

def logout():
    user = User()
    name=user.get_name(getUserIdFromEmail(flask_login.current_user.id))
    if name == None:
        name = ""
    flask_login.logout_user()
    return render_template('index.html', message='Goodbye '+name+'!',logged_in=flask_login.current_user.is_authenticated)

def unauthorized_handler():
    return render_template('unauth.html',logged_in=flask_login.current_user.is_authenticated)

def register():
    return render_template('register.html', supress='True',logged_in=flask_login.current_user.is_authenticated)

def register_user():
    user = User()
    try:
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        email=request.form.get('email')
        password=request.form.get('password')
    except:
        print("couldn't find all tokens")
        return render_template("register.html", suppress=False, message="Please try again!")
    print(first_name)
    if first_name == "" or last_name == "" or email == "" or password == "":
        return render_template("register.html", suppress=False, message="All fields are required.")
    cursor = conn.cursor()
    unique =  isEmailUnique(email)
    valid = re.match(r"[^@]+@[^@]+\.[^@]+", email)
    if unique and valid:
        user.create_user(first_name, last_name, email, password)
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('index.html', name=first_name, message='Account Created!',logged_in=flask_login.current_user.is_authenticated)
    else:
        print("couldn't find all tokens")
        return render_template("register.html", suppress=False, message="Please try again with a unique and valid email!", logged_in=flask_login.current_user.is_authenticated)




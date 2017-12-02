from flask import Flask, render_template, request, redirect, url_for, session, escape
from flaskext.mysql import MySQL
import flask_login

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

class User(flask_login.UserMixin):
    def __init__(self):
        app = Flask(__name__)
        self.mysql = MySQL()
        app.config.from_pyfile('config.cfg')
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()

    # returns user_id of user who was just created
    def create_user(self, username, password):
        #user_id must be unique
        cursor = self.conn.cursor()
        query = "INSERT INTO Users(username, password) VALUES ('{0}', '{1}')".format(username, password)
        cursor.execute(query)
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


    def get_user_id_from_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE username = '{0}'".format(username))
        response = cursor.fetchone()[0]
        return response

    def get_username(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM Users WHERE user_id = '{0}'".format(user_id))
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
    pwd = str(data[0][0] )
    user.is_authenticated = request.form['password'] == pwd
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
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a>
               '''
    #The request method is POST (page is recieving data)
    email = request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        if request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            print(user.is_active,user.is_authenticated,user.is_anonymous,user.get_id)
            return render_template('index.html', message='Logged in!')
 

    #information did not match
    return "<a href='/login'>Try again</a>\
            </br><a href='/register'>or make an account</a>"

def logout():
    flask_login.logout_user()
    return render_template('index.html', message='Logged out')

def unauthorized_handler():
    return render_template('unauth.html')

def register():
    return render_template('register.html', supress='True')

def register_user():
    try:
        username=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
    except:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    unique =  isEmailUnique(email)
    if unique:
        cursor.execute("INSERT INTO Users (username, email, password) VALUES ('{0}', '{1}', '{2}')".format(username, email, password))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('index.html', name=username, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return render_template("register.html", suppress=False)



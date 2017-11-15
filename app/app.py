from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import json
from likes import Likes
from user import User
from dislikes import Dislikes
from tokens import Tokens
from random import randint
import twitter
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

#mySQL loading (might want to keep it in the separate py files though)
mysql = MySQL()
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mysql.init_app(app)

#our site login management
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

#user info
likes = Likes()
user = User()
dislikes = Dislikes()
tokens = Tokens()

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

### modulate this out
def getUsers():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()

class User(flask_login.UserMixin):
    # stub for now, no function
    pass

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

###

@app.route("/")
def main():
    test_database_calls()
    return render_template('index.html')

###
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
           <a href='/'>Home</a>
               '''
    #The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    #check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0] )
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) #okay login in user
            return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file
 
    #information did not match
    return "<a href='/login'>Try again</a>\
            </br><a href='/register'>or make an account</a>"
 
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('index.html', message='Logged out', users=findTopUsers())
 
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')
 
#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')  
 
@app.route("/register", methods=['POST'])
def register_user():
    try:
        email=request.form.get('email')
        password=request.form.get('password')
        username=request.form.get('name')
    except:
        print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test =  isEmailUnique(email)
    if test:
        cursor.execute("INSERT INTO Users (name, email, password) VALUES ('{0}', '{1}', '{2}')".format(name, email, password))
        conn.commit()
        #log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('profile.html', name=username, message='Account Created!')
    else:
        print "couldn't find all tokens"
        return render_template("register.html", suppress=False)


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    if cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email)):
        return cursor.fetchone()[0]
    else:
        return None
 
def isEmailUnique(email):
    #use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        return False
    else:
        return True
###
    
@app.route("/giphy", methods=["POST"])
def call_giphy_api():
    search_value = request.form.get('keyword')
    # pass parsed api contents in `result` to html
    api_key = app.config['GFY_KEY']
    data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+("+".join(search_value.split(" "))) +"&api_key="+ api_key +"&limit=5").read())
    print(data)
    urls = []
    
    # if there are no gifs, display 404 gifs
    if data["data"] == []:
        data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+ "404" + "&api_key="+ api_key +"&limit=5").read())
    
    # pass in list of embedded urls for html to display
    for element in data["data"]:
        urls += [element["embed_url"]]
    return render_template('index.html', result=urls)

# examples of how to call the database
def test_database_calls():
    random_user = randint(1, 1000)
    user_id = user.create_user('test_user' + str(random_user), 'asidf38iawef8y')
    username = user.get_username(user_id)
    print(username)
    print(user.get_user_id_from_username(username))

    user.set_twitter_username(user_id, 'test_username')
    print(user.get_twitter_info(user_id))

    likes.set_likes(user_id, 'http')
    print(likes.get_likes(user_id))

    dislikes.set_dislikes(user_id, 'http')
    print(dislikes.get_dislikes(user_id))

@app.route("/twitter/auth",methods=["GET"])
def twitter_auth():
	return twitter.authorize_init(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'])

@app.route("/twitter/",methods=["GET"])
def get_twitter_token():
    token = request.args.get("oauth_token",None)
    verifier = request.args.get("oauth_verifier",None)
    response = twitter.authorize_final(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],token,verifier)
    
    # change this once we get a real user id from the native login
    user_id = 1
    token = response[0].split("=")[1]
    secret = response[1].split("=")[1]
    tokens.set_oauth_twitter_tokens(user_id, token, secret)
    twitter_user_id = response[2].split("=")[1]
    screen_name = response[3].split("=")[1]
    user.set_twitter_username(user_id, screen_name)
    user.set_twitter_id(user_id, twitter_user_id)
    expires = response[4]
    print("Twitter Auth Info:")
    print(response)

    return render_template('index.html')

if __name__ == "__main__":
    app.run()

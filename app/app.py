from flask import Flask, render_template, request, redirect, url_for, session, escape
from flaskext.mysql import MySQL
import flask_login
import json
from likes import Likes
from user import User
from dislikes import Dislikes
from tokens import Tokens
from random import randint
import twitter
import loginmanagement
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
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return loginmanagement.login()
 
@app.route('/logout')
def logout():
    return loginmanagement.logout()
 
@login_manager.unauthorized_handler
def unauthorized_handler():
    return loginmanagement.unauthorized_handler()
 
#we can specify specific methods (GET/POST) in function header
@app.route("/register", methods=['GET'])
def register():
    return registration.register()
 
@app.route("/register", methods=['POST'])
def register_user():
    return loginmanagement.register_user()
    
@flask_login.login_required
@app.route("/giphy", methods=["POST"])
#@flask_login.login_required
def call_giphy_api(search=None):
    message = ""
    if search == None:
        search_value = request.form.get('keyword')
    else:
        search_value = search
    # pass parsed api contents in `result` to html
    api_key = app.config['GFY_KEY']
    data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+("+".join(search_value.split(" "))) +"&api_key="+ api_key +"&limit=5").read())
    print(data)
    urls = []

    # if there are no gifs, display 404 gifs
    if data["data"] == []:
        data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+ "404" + "&api_key="+ api_key +"&limit=5").read())
        message="Sorry, we couldn't find any GIFs!"
    # pass in list of embedded urls for html to display
    for element in data["data"]:
        urls += [element["embed_url"]]
    return render_template('index.html', result=urls,tones=search_value,message=message)

@app.route("/page/login", methods=["GET"])
def show_login_page():
    return render_template("login.html")

@app.route("/page/register",methods=["GET"])
def show_register_page():
    return render_template("register.html")

@app.route("/page/likes", methods=["GET"])
def show_likes_page():
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    urls = [likes[0] for likes in likes.get_likes(uid)]
    return render_template("likes.html", result=urls)

@login_manager.user_loader
def user_loader(email):
  return loginmanagement.user_loader(email)

@login_manager.request_loader
def request_loader(request): 
  return loginmanagement.request_loader(request)

@app.route('/page/likes', methods=['POST'])
#@flask_login.login_required
def like_gif():
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        embedded_url = request.form.get('likes')
        likes.set_likes(uid, embedded_url)
    return render_template('index.html')

@app.route('/page/dislikes', methods=['POST'])
#@flask_login.login_required
def dislike_gif():
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    embedded_url = request.form.get('dislikes')
    if request.method == 'POST':
        embedded_url = request.form.get('dislikes')
        dislikes.set_dislikes(uid, embedded_url)
        
    return render_template('index.html')


@app.route("/twitter/auth",methods=["GET"])
@flask_login.login_required
def twitter_auth():
	return redirect(twitter.authorize_init(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET']))

@app.route("/twitter/",methods=["GET"])
@flask_login.login_required
def get_twitter_token():
    token = request.args.get("oauth_token",None)
    print(token)
    verifier = request.args.get("oauth_verifier",None)
    print(verifier)
    response = twitter.authorize_final(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],token,verifier)
    print("Twitter Auth Info:")
    print(response)
    # change this once we get a real user id from the native login
    user_id = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
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
    tweets = twitter.get_tweets(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],1,20)
    print(tweets)
    tones = twitter.get_tone(app.config['IBM_USERNAME'],app.config['IBM_PASSWORD'],tweets)
    return call_giphy_api(search=tones)

if __name__ == "__main__":
    app.run()

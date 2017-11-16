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
<<<<<<< HEAD

=======
>>>>>>> refs/remotes/origin/master

@app.route("/")
def main():
    test_database_calls()
    return render_template('index.html')

@app.route("/giphy", methods=["POST"])
def call_giphy_api(search=None):
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

    # pass in list of embedded urls for html to display
    for element in data["data"]:
        urls += [element["embed_url"]]
    return render_template('index.html', result=urls,tones=search_value)

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
    tweets = twitter.get_tweets(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],1,20)
    tones = twitter.get_tone(app.config['IBM_USERNAME'],app.config['IBM_PASSWORD'],tweets)
    return call_giphy_api(search=tones)

if __name__ == "__main__":
    app.run()

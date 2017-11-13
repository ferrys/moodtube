from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import json
from likes import Likes
from user import User
from dislikes import Dislikes
from random import randint
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

#loading, env variables
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

#our site login management
login_manager = LoginManager()
login_manager.init_app(app)

#user info
likes = Likes()
user = User()
dislikes = Dislikes()

@app.route("/")
def main():
    test_database_calls()
    return render_template('index.html')

@app.route("/giphy", methods=["POST"])
def call_giphy_api():
    search_value = request.form.get('keyword')
    # pass parsed api contents in `result` to html
    api_key = app.config['GFY_KEY']
    data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+("+".join(search_value.split(" "))) +"&api_key="+ api_key +"&limit=5").read())
    urls = []
    # pass in list of embedded urls for html to display
    for element in data["data"]:
        urls += [element["embed_url"]]
    return render_template('index.html', result=urls)


def test_database_calls():
    random_user = randint(1, 1000)
    user_id = user.create_user('test_user' + str(random_user), 'asidf38iawef8y')
    username = user.get_username(user_id)
    print(username)
    print(user.get_user_id_from_username(username))

    user.set_twitter_username(user_id, 'test_username')
    user.set_twitter_api_key(user_id, '8owaeifs98y32ohr8yewohif')
    print(user.get_twitter_info(user_id))

    likes.set_likes(user_id, 'http')
    print(likes.get_likes(user_id))

    dislikes.set_dislikes(user_id, 'http')
    print(dislikes.get_dislikes(user_id))

@app.route("/twitter/auth",methods=["GET"])
def twitter_auth():
	return twitter.authorize_init()

@app.route("/twitter/",methods=["GET"])
def get_twitter_token():
    token = request.args.get("oauth_token",None)
    verifier = request.args.get("oauth_verifier",None)
    response = twitter.authorize_final(token,verifier)

    token = response[0]
    secret = response[1]
    user_id = resonse[2]
    screen_name = response[3]
    expires = response[4]

    print(twitter.authorize_final(token,verifier))

    return redirect("/")

if __name__ == "__main__":
    app.run()

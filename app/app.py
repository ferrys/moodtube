from flask import Flask, render_template, request, redirect, url_for, session, escape
from flaskext.mysql import MySQL
import flask_login
import json
from likes import Likes
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
user = loginmanagement.User()
dislikes = Dislikes()
tokens = Tokens()

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()

@app.route("/")
def main():
    return render_template('index.html',logged_in=flask_login.current_user.is_authenticated)




####### LOGIN #######
@app.route('/login', methods=['GET', 'POST'])
def login():
    return loginmanagement.login()

@app.route('/logout')
def logout():
    return loginmanagement.logout()

@login_manager.unauthorized_handler
def unauthorized_handler():
    return loginmanagement.unauthorized_handler()

@app.route("/register", methods=['POST'])
def register_user():
    return loginmanagement.register_user()

@login_manager.user_loader
def user_loader(email):
  return loginmanagement.user_loader(email)

@login_manager.request_loader
def request_loader(request):
  return loginmanagement.request_loader(request)

###### END LOGIN ######



####### GIPHY #######
@app.route("/giphy", methods=["POST"])
@flask_login.login_required
def call_giphy_api(search=None, message=''):
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    if search == None:
        search_value = request.form.get('keyword')
    else:
        search_value = search
    # pass parsed api contents in `result` to html
    api_key = app.config['GFY_KEY']
    data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+("+".join(search_value.split(" "))) +"&api_key="+ api_key +"&limit=20").read())
    print(data)
    urls = []

    # if there are no gifs, display 404 gifs
    if data["data"] == []:
        data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+ "404" + "&api_key="+ api_key +"&limit=5").read())
        message="Sorry, we couldn't find any GIFs!"
    # pass in list of embedded urls for html to display
    for element in data["data"]:
        print(likes.find_like(uid, element["embed_url"]))
        like_text = "Unlike!" if likes.find_like(uid, element["embed_url"]) != () else "Like!"
        dislike_text = "Un-dislike!" if dislikes.find_dislike(uid, element["embed_url"]) != () else "Dislike!"
        urls += [(element["embed_url"], like_text, dislike_text, search_value)]
    print(urls)
    return render_template('index.html', result=urls,tones=search_value,message=message,logged_in=flask_login.current_user.is_authenticated)

##### END GIPHY ########



###### SHOW PAGES ########

@app.route("/page/login", methods=["GET"])
def show_login_page():
    return render_template("login.html",logged_in=flask_login.current_user.is_authenticated)

@app.route("/page/register",methods=["GET"])
def show_register_page():
    return render_template("register.html",logged_in=flask_login.current_user.is_authenticated)

@app.route("/page/likes", methods=["GET"])
@flask_login.login_required
def show_likes_page():
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    urls = [x[0] for x in likes.get_likes(uid)]
    urls = reversed(urls)
    return render_template("likes.html", result=urls, message="Likes!", logged_in=flask_login.current_user.is_authenticated)

@app.route("/page/dislikes", methods=["GET"])
@flask_login.login_required
def show_dislikes_page():
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    urls = [x[0] for x in dislikes.get_dislikes(uid)]
    urls = reversed(urls)
    return render_template("dislikes.html", result=urls, message="Dislikes!", logged_in=flask_login.current_user.is_authenticated)

@app.route("/moodchoose", methods=["GET"])
@flask_login.login_required
def show_moodchoose_page():
    return render_template("moodchoose.html",logged_in=flask_login.current_user.is_authenticated)

###### END SHOW PAGES########


#### LIKES / DISLIKES ####
@app.route('/page/likes', methods=['POST'])
@flask_login.login_required
def like_unlike():
    if request.method == 'POST':
        embedded_url = request.form.get('likes')
        like_value = request.form.get('like_value')
        search = request.form.get("tone")
        if like_value == "Like!":
            return like_gif(embedded_url, search)
        else:
            return unlike_gif(embedded_url,search)

def like_gif(embedded_url, search):
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    likes.set_likes(uid, embedded_url)
    if search == 'N/A':
        return show_likes_page()
    return call_giphy_api(search, message="GIF Liked!")

def unlike_gif(embedded_url, search):
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    likes.remove_like(uid, embedded_url)
    if search == 'N/A':
        return show_likes_page()
    return call_giphy_api(search, message="GIF Unliked!")


@app.route('/page/dislikes', methods=['POST'])
@flask_login.login_required
def dislike_undislike():
    if request.method == 'POST':
        embedded_url = request.form.get('dislikes')
        like_value = request.form.get('dislike_value')
        search = request.form.get("tone")
        if like_value == "Dislike!":
            return dislike_gif(embedded_url, search)
        else:
            return undislike_gif(embedded_url, search)

def undislike_gif(embedded_url, search):
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    dislikes.remove_dislike(uid, embedded_url)
    if search == 'N/A':
        return show_dislikes_page()
    return call_giphy_api(search, message="GIF Un-disliked!")

def dislike_gif(embedded_url, search):
    uid = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    dislikes.set_dislikes(uid, embedded_url)
    if search == 'N/A':
        return show_dislikes_page()
    return call_giphy_api(search, message="GIF Disliked!")

#### END / DISLIKES ####





##### TWITTER ######
@app.route("/twitter/auth",methods=["GET"])
@flask_login.login_required
def twitter_auth():
    user_id = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    return redirect(twitter.authorize_init(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],user_id))

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
    tweets = twitter.get_tweets(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],user_id,20)
    print(tweets)
    tones = twitter.get_tone(app.config['IBM_USERNAME'],app.config['IBM_PASSWORD'],tweets)
    return call_giphy_api(search=tones)

@app.route("/tweet",methods=["POST"])
@flask_login.login_required
def tweet():
    user_id = loginmanagement.getUserIdFromEmail(flask_login.current_user.id)
    tweet = request.form.get('tweet')
    source = request.form.get('from')

    print("Twitter Post Response:")
    print(twitter.post_tweet(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],user_id,tweet))
    if source == "index":
        tweets = twitter.get_tweets(app.config['TWITTER_KEY'],app.config['TWITTER_SECRET'],user_id,20)
        tones = twitter.get_tone(app.config['IBM_USERNAME'],app.config['IBM_PASSWORD'],tweets)
        return call_giphy_api(search=tones)
    elif source == "likes":
        return show_likes_page()
    elif source == "dislikes":
        return show_dislikes_page()
##### END TWITTER ######

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', logged_in=flask_login.current_user.is_authenticated), 500
@app.errorhandler(404)
def page_not_found(e):
    return render_template('500.html', logged_in=flask_login.current_user.is_authenticated), 404

if __name__ == "__main__":
    app.run()

from flask import Flask, render_template, request
import json
from urllib.request import urlopen
from likes import Likes
from user import User
from dislikes import Dislikes
from random import randint

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
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
    api_key = app.config['API_KEY']
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

if __name__ == "__main__":
    app.run()

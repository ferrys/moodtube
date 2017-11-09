from flask import Flask, render_template, request
import json
from urllib.request import urlopen
from likes import Likes
from user import User
from random import randint
from dislikes import Dislikes

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
likes = Likes()
user = User()
dislikes = Dislikes()

@app.route("/")
def main():
    test_call_database()
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

def test_call_database():
    user_id = randint(1,10000)
    print(user_id)
    user.set_user(user_id, 'test', 'asidf38iawef8y')
    print(user.get_user(user_id))
    likes.set_likes(user_id, 'http')
    print(likes.get_likes(user_id))
    dislikes.set_dislikes(user_id, 'http')
    print(dislikes.get_dislikes(user_id))

if __name__ == "__main__":
    app.run()

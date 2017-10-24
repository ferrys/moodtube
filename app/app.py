from flask import Flask, render_template, request
import json
from urllib.request import urlopen

app = Flask(__name__)

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/giphy", methods=["POST"])
def call_giphy_api():
	search_value = request.form.get('keyword')
	# pass parsed api contents in `result` to html
	api_key = get_api_key("creds.txt")
	data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+("+".join(search_value.split(" "))) +"&api_key="+ api_key +"&limit=5").read())
	urls = []
	for element in data["data"]:
		urls += [element["embed_url"]]
	return render_template('index.html', result=urls)

def get_api_key(file_name):
	f = open(file_name, "r")
	txt = f.read()
	f.close()

	api_key = txt.split("=")[1]
	return api_key

if __name__ == "__main__":
	app.run()

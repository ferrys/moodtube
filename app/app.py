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
	# call giphy api here! 
	# pass parsed api contents in `result` to html
	data = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q="+("+".join(search_value.split(" ")))        +"&api_key=apikeyhere&limit=5").read())
	print(json.dumps(data, sort_keys=True, indent=4))
	result = json.dumps(data, sort_keys=True, indent=4)
	print("+".join(search_value.split(" ")))
	return render_template('index.html', result=result)

if __name__ == "__main__":
	app.run()

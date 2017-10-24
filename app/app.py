from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/giphy", methods=["POST"])
def call_giphy_api():
	search_value = request.form.get('keyword')
	# call giphy api here! 
	# pass parsed api contents in `result` to html
	print(search_value)
	return render_template('index.html', result=search_value)

if __name__ == "__main__":
	app.run()

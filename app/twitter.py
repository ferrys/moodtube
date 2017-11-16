import oauth2 as oauth
from tokens import Tokens
import user
import json
from watson_developer_cloud import ToneAnalyzerV3

#steps 1 and 2 of authorization
def authorize_init(key, secret):
	# Create your consumer with the proper key/secret.
	consumer = oauth.Consumer(key=key, secret=secret)

	# Request token URL for Twitter.
	request_token_url = "https://api.twitter.com/oauth/request_token"

	# Create our client.
	client = oauth.Client(consumer)

	# The OAuth Client request works just like httplib2 for the most part.
	resp, content = client.request(request_token_url, "GET")
	#print(resp["oauth_token"])
	oauth_token = str(content)[1:].split("&")[0].split("=")[1]
	oauth_secret = str(content)[1:].split("&")[1].split("=")[1]
	print(oauth_token,oauth_secret)
	db = Tokens()
	db.set_temp_twitter_key(1, oauth_token,oauth_secret)
	print(db.get_temp_twitter_key(oauth_token))

	url = "https://api.twitter.com/oauth/authenticate"
	token = oauth.Token(key=oauth_token, secret=oauth_secret)
	client = oauth.Client(consumer, token)
	resp, content = client.request(url, "GET")
	#print(resp)

	return content.decode("utf-8")

#step 3 of authorization
def authorize_final(key, secret, token, verifier):
	url = "https://api.twitter.com/oauth/access_token"

	consumer = oauth.Consumer(key=key, secret=secret)
	db = Tokens()
	secret = db.get_temp_twitter_key(token)
	token = oauth.Token(key=token, secret=secret)
	token.set_verifier(verifier)
	client = oauth.Client(consumer,token)
	resp,content = client.request(url,"POST")
	content.decode("utf-8")
	db.del_temp_twitter_key(token)
	return content.decode("utf-8").split("&")

def get_tweets(key,secret,user_id,number):
	if(number >3200):
		number = 3200
	db = user.User()
	screen_name = db.get_twitter_info(user_id)
	print(screen_name)
	url = generate_url(screen_name,number,None)
	consumer = oauth.Consumer(key=key, secret=secret)
	db = Tokens()
	token = db.get_oauth_twitter_tokens(user_id)
	key = token[0]
	secret = token[1]
	twitter_token = oauth.Token(key,secret)
	client = oauth.Client(consumer, twitter_token)
	resp,content = client.request(url,"GET")

	tweets = []
	remaining = number

	while remaining > 0:
		resp,content = client.request(url,"GET")
		jsoned = json.loads(content)
		if len(tweets) != 0:
			jsoned = jsoned[1:]
		if len(jsoned) == 0:
			break
		tweets+=jsoned
		remaining -= len(jsoned)
		url = generate_url(screen_name,remaining,jsoned[-1]["id_str"])
	print(len(tweets))
	text = ""
	for i in tweets:
		text+= i["text"]+"\n"
	return text

def generate_url(screen_name,count,max_id):
	url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name="
	url+=screen_name
	url+="&count="
	if count > 200:
		url+="200"
	else:
		url+=str(count)
	if max_id != None:
		url+="&max_id="
		url+=max_id
	return url


def get_tone(username, password, text):
	url = "https://gateway.watsonplatform.net/authorization/api/v1/token"
	tone_analyzer = ToneAnalyzerV3(
  		version='2017-09-21',
  		username=username,
  		password=password
	)
	response = tone_analyzer.tone(text, tones='emotion', content_type='text/plain')
	print(response)
	tones_json = response["document_tone"]["tones"]
	tones_list = []

	for tone in tones_json:
		tones_list += [tone["tone_name"]]

	return " ".join(tones_list)

if __name__ == "__main__":
	authorize_init()

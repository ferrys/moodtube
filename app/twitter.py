import oauth2 as oauth
from tokens import Tokens

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


if __name__ == "__main__":
	authorize_init()

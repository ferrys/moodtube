from flask import Flask
from flaskext.mysql import MySQL
class Tokens(object):
    def __init__(self):
        app = Flask(__name__)
        self.mysql = MySQL()
        app.config.from_pyfile('config.cfg')
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()

    def get_temp_twitter_key(self, request_token):
        cursor = self.conn.cursor()
        cursor.execute("SELECT request_secret FROM Tokens WHERE request_token = '{0}'".format(request_token))
        secret = response = cursor.fetchone()[0]
        return secret

    def set_temp_twitter_key(self,user_id, request_token, request_secret):
        cursor = self.conn.cursor()
        query = "INSERT INTO Tokens(user_id, request_token, request_secret) VALUES ('{0}', '{1}', '{2}')".format(user_id, request_token, request_secret)
        cursor.execute(query)
        self.conn.commit()

    def del_temp_twitter_key(self,request_token):
        cursor = self.conn.cursor()
        query = "DELETE FROM Tokens WHERE request_token='{0}'".format(request_token)
        cursor.execute(query)
        self.conn.commit()
        
    def set_oauth_twitter_tokens(self, user_id, oauth_token, oauth_token_secret):
        cursor = self.conn.cursor()
        query = "UPDATE Tokens SET oauth_token = '{0}', oauth_token_secret = '{1}' WHERE user_id = '{2}'".format(oauth_token, oauth_token_secret, user_id)
        cursor.execute(query)
        self.conn.commit()
        
        
        
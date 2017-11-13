from flask import Flask
from flaskext.mysql import MySQL
class User(object):
    def __init__(self):
        app = Flask(__name__)
        self.mysql = MySQL()
        app.config.from_pyfile('config.cfg')
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()

    # returns user_id of user who was just created
    def create_user(self, username, password):
        #user_id must be unique
        cursor = self.conn.cursor()
        query = "INSERT INTO Users(username, password) VALUES ('{0}', '{1}')".format(username, password)
        cursor.execute(query)
        self.conn.commit()
        return cursor.lastrowid

    def set_twitter_username(self, user_id, twitter_username):
        cursor = self.conn.cursor()
        query = "UPDATE Users SET twitter_username = '{0}' WHERE user_id = {1}".format(twitter_username, user_id)
        cursor.execute(query)
        self.conn.commit()

    def set_twitter_api_key(self, user_id, twitter_api_key):
        cursor = self.conn.cursor()
        query = "UPDATE Users SET twitter_api_key = '{0}' WHERE user_id = {1}".format(twitter_api_key, user_id)
        cursor.execute(query)
        self.conn.commit()

    def get_user_id_from_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE username = '{0}'".format(username))
        response = cursor.fetchone()[0]
        return response

    def get_username(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM Users WHERE user_id = '{0}'".format(user_id))
        response = cursor.fetchone()[0]
        return response

    # returns twitter_username, twitter_api_key
    def get_twitter_info(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT twitter_username, twitter_api_key FROM Users WHERE user_id = '{0}'".format(user_id))
        response = cursor.fetchone()
        return response[0], response[1]

    def get_temp_twitter_key(self,request_token):
        cursor = self.conn.cursor()
        cursor.execute("SELECT request_secret FROM Tokens WHERE request_token = '{0}'".format(request_token))
        secret = response = cursor.fetchone()[0]
        return secret

    def set_temp_twitter_key(self,request_token, request_secret):
        cursor = self.conn.cursor()
        query = "INSERT INTO Tokens(request_token, request_secret) VALUES ('{0}', '{1}')".format(request_token, request_secret)
        cursor.execute(query)
        self.conn.commit()

    def del_temp_twitter_key(self,request_token):
        cursor = self.conn.cursor()
        query = "DELETE FROM Tokens WHERE request_token='{0}'".format(request_token)
        cursor.execute(query)
        self.conn.commit()

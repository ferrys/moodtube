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
        
    def set_twitter_id(self, user_id, twitter_id):
        cursor = self.conn.cursor()
        query = "UPDATE Users SET twitter_user_id = '{0}' WHERE user_id = {1}".format(twitter_id, user_id)
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
        cursor.execute("SELECT twitter_username FROM Users WHERE user_id = '{0}'".format(user_id))
        response = cursor.fetchone()
        return response[0]



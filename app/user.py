from flask import Flask
from flaskext.mysql import MySQL
class User(object):
    def __init__(self):
        app = Flask(__name__)
        self.mysql = MySQL()
        app.config.from_pyfile('config.cfg')
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()
    
    def set_user(self, user_id, twitter_username, twitter_api_key):
        #user_id must be unique
        cursor = self.conn.cursor()
        query = "INSERT INTO Users(user_id, twitter_username, twitter_api_key) VALUES ({0}, '{1}', '{2}')".format(user_id, twitter_username, twitter_api_key)
        cursor.execute(query)
        self.conn.commit()

    # returns twitter_username, twitter_api_key
    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT twitter_username, twitter_api_key FROM Users WHERE user_id = '{0}'".format(user_id))
        response = cursor.fetchone()
        return response[0], response[1]
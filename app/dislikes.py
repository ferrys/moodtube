from flask import Flask
from flaskext.mysql import MySQL
class Dislikes(object):
    def __init__(self):
        app = Flask(__name__)
        self.mysql = MySQL()
        app.config.from_pyfile('config.cfg')
        self.mysql.init_app(app)
        self.conn = self.mysql.connect()
    
    def set_dislikes(self, user_id, gif_url):
        #user_id foreign key to users 
        #so must have corresponding user
        cursor = self.conn.cursor()
        query = "INSERT INTO Dislikes(user_id, gif_url) VALUES ({0}, '{1}')".format(user_id, gif_url)
        cursor.execute(query)
        self.conn.commit()

    def get_dislikes(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT gif_url FROM Dislikes WHERE user_id = '{0}'".format(user_id))
        return cursor.fetchall()
    
    def find_dislike(self, user_id, gif_url):
        cursor = self.conn.cursor()
        cursor.execute("SELECT gif_url FROM Dislikes WHERE user_id = '{0}' AND gif_url = '{1}'".format(user_id, gif_url))
        return cursor.fetchall()
    
    def remove_dislike(self, user_id, gif_url):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Dislikes WHERE user_id = '{0}' AND gif_url = '{1}'".format(user_id, gif_url))
        self.conn.commit()
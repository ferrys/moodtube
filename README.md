# moodtube
Group project for CS 411

### To run app:

`pip install flask`

`pip install oauth2`

`pip install flask-login`

`pip install --upgrade watson-developer-cloud`

`python app.py`


go to localhost:5000

### To configure database
- Download MySQl (https://dev.mysql.com/downloads/mysql/)
- Install the flask connector `pip install flask-mysql`

### Config file:
- Create file named `config.cfg`
- The contents should be:
```
GFY_KEY='your-api-key'
MYSQL_DATABASE_USER='root'
MYSQL_DATABASE_PASSWORD='your-password'
MYSQL_DATABASE_DB='moodtube'
MYSQL_DATABASE_HOST='localhost'
TWITTER_KEY='your-api-key'
TWITTER_SECRET='your-api-key-secret'
IBM_USERNAME='username'
IBM_PASSWORD='password'
```

from app import app
import urllib
import os

# secret key for user session
app.secret_key = "ITSASECRET"

#setting up mail
# app.config['MAIL_SERVER']='' #mail server
# app.config['MAIL_PORT'] = 587 #mail port
# app.config['MAIL_USERNAME'] = '' #email
# app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD'] #password
# app.config['MAIL_USE_TLS'] = True #security type
# app.config['MAIL_USE_SSL'] = False #security type

#database connection parameters
connection_params = {
    # 'user': '',
    # 'password': os.environ['DB_PASSWORD'],
    'host': 'localhost',
    'port': '27017',
    'namespace': '',
}

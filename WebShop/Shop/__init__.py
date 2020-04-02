from flask import Flask
from pymongo import MongoClient
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
password = os.environ['MYSQL_ROOT_PASSWORD']
db = os.environ['MYSQL_DATABASE']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:'+password+'@172.18.0.1:3306/'+db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/imse_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
client = MongoClient('mongodb://mongo:27017')
mongo = client.imse

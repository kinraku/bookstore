import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://bookuser:password@localhost/bookstore'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
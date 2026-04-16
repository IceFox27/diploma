import os

class Config(object):
    APPNAME = 'app'
    ROOT = os.path.abspath(APPNAME)
    UPLOAD_PATH = '/static/upload/'
    SERVER_PATH = ROOT + UPLOAD_PATH

    USER = os.environ.get('POSTGRES_USER', 'icefox')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', "27xx69alphaCoder")
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', 5532)
    DB = os.environ.get('POSTGRES_DB', 'myhousedv')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = '59287JFHIajgrgkn52ofspkvsbs4'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
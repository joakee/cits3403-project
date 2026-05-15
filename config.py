import os
from dotenv import load_dotenv

# This looks for a .env file in the current directory
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'marketplace.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB upload limit
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    MAIL_USERNAME = 'apikey' 
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY') 
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-prod'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'marketplace.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB upload limit
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')

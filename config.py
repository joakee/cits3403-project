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
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    MAIL_USERNAME = os.environ.get('BREVO_EMAIL')
    MAIL_PASSWORD = os.environ.get('BREVO_PASSWORD') 
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Microsoft Entra ID / Azure AD SSO
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    # Use 'common' for multi-tenant during dev. For UWA-only, set to UWA's tenant ID.
    MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID', 'common')
    MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_REDIRECT_URI', 'http://localhost:5000/auth/microsoft/callback')
    # Comma-separated allowlist of email domains
    SSO_ALLOWED_EMAIL_DOMAINS = os.environ.get(
        'SSO_ALLOWED_EMAIL_DOMAINS',
        'uwa.edu.au,student.uwa.edu.au'
    ).split(',')

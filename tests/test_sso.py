"""Unit tests for Microsoft SSO helpers and routes."""
import pytest
from flask import current_app
from app.routes.sso import _email_domain_allowed, _unique_username


class TestEmailDomainAllowed:
    def test_uwa_edu_au(self, app):
        with app.app_context():
            assert _email_domain_allowed('foo@uwa.edu.au') is True

    def test_student_uwa_edu_au(self, app):
        with app.app_context():
            assert _email_domain_allowed('bar@student.uwa.edu.au') is True

    def test_case_insensitive(self, app):
        with app.app_context():
            assert _email_domain_allowed('User@UWA.EDU.AU') is True

    def test_gmail_rejected(self, app):
        with app.app_context():
            assert _email_domain_allowed('evil@gmail.com') is False

    def test_empty_string(self, app):
        with app.app_context():
            assert _email_domain_allowed('') is False

    def test_none(self, app):
        with app.app_context():
            assert _email_domain_allowed(None) is False

    def test_no_atsign(self, app):
        with app.app_context():
            assert _email_domain_allowed('noatsign') is False


class TestUniqueUsername:
    def test_basic(self, app):
        with app.app_context():
            result = _unique_username('testuser')
            assert result == 'testuser'

    def test_collision_appends_suffix(self, app):
        from app import db
        from app.models import User
        from werkzeug.security import generate_password_hash
        with app.app_context():
            existing = User(
                username='collision',
                email='collision@example.com',
                password_hash=generate_password_hash('pw', method='pbkdf2:sha256'),
            )
            db.session.add(existing)
            db.session.commit()
            result = _unique_username('collision')
            assert result == 'collision2'

    def test_strips_spaces_and_lowercases(self, app):
        with app.app_context():
            result = _unique_username(' Test User ')
            assert result == 'testuser'

    def test_empty_base_defaults_to_user(self, app):
        with app.app_context():
            result = _unique_username('')
            assert result == 'user'


class TestSSORoutes:
    def test_login_redirect_when_authenticated(self, app, client):
        with app.app_context():
            from app import db
            from app.models import User
            from werkzeug.security import generate_password_hash
            user = User(
                username='ssotest',
                email='ssotest@uwa.edu.au',
                password_hash=generate_password_hash('pw', method='pbkdf2:sha256'),
                is_verified=True,
            )
            db.session.add(user)
            db.session.commit()
            uid = user.id

        with client.session_transaction() as sess:
            sess['_user_id'] = str(uid)
            sess['_fresh'] = True

        resp = client.get('/auth/microsoft/login', follow_redirects=False)
        assert resp.status_code == 302

    def test_callback_without_code_redirects_to_login(self, client):
        resp = client.get('/auth/microsoft/callback', follow_redirects=True)
        assert resp.status_code == 200
        assert b'Log In' in resp.data

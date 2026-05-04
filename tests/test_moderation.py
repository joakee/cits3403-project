import pytest
from app import db
from app.models import User, Listing, Report
from tests.conftest import login


class TestReportCreation:
    def test_report_listing_authenticated(self, client, regular_user, admin_user, sample_listing):
        """A logged-in user can report a listing they don't own."""
        login(client, 'admin@example.com')
        resp = client.post(f'/moderation/report/listing/{sample_listing}', data={
            'reason': 'spam',
            'description': 'This looks like spam',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Report submitted' in resp.data

    def test_report_listing_unauthenticated(self, client, sample_listing):
        """Unauthenticated user is redirected to login."""
        resp = client.get(f'/moderation/report/listing/{sample_listing}')
        assert resp.status_code == 302
        assert '/auth/login' in resp.headers['Location']

    def test_cannot_report_own_listing(self, client, regular_user, sample_listing):
        """User cannot report their own listing."""
        login(client, 'test@example.com')
        resp = client.get(f'/moderation/report/listing/{sample_listing}', follow_redirects=True)
        assert b'cannot report your own listing' in resp.data

    def test_duplicate_report_blocked(self, client, regular_user, admin_user, sample_listing):
        """Duplicate open reports for same target by same user are blocked."""
        login(client, 'admin@example.com')
        client.post(f'/moderation/report/listing/{sample_listing}', data={
            'reason': 'spam',
        }, follow_redirects=True)
        resp = client.post(f'/moderation/report/listing/{sample_listing}', data={
            'reason': 'scam',
        }, follow_redirects=True)
        assert b'already have an open report' in resp.data

    def test_report_user(self, client, regular_user, admin_user):
        """A user can report another user."""
        login(client, 'admin@example.com')
        resp = client.post(f'/moderation/report/user/{regular_user}', data={
            'reason': 'scam',
            'description': 'Suspicious behavior',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Report submitted' in resp.data

    def test_cannot_report_self(self, client, regular_user):
        """User cannot report themselves."""
        login(client, 'test@example.com')
        resp = client.get(f'/moderation/report/user/{regular_user}', follow_redirects=True)
        assert b'cannot report yourself' in resp.data


class TestAdminAccess:
    def test_regular_user_cannot_access_reports(self, client, regular_user):
        """Non-admin/mod users get 403 on reports list."""
        login(client, 'test@example.com')
        resp = client.get('/moderation/reports')
        assert resp.status_code == 403

    def test_admin_can_access_reports(self, client, admin_user):
        """Admin can access the reports list."""
        login(client, 'admin@example.com')
        resp = client.get('/moderation/reports')
        assert resp.status_code == 200

    def test_moderator_can_access_reports(self, client, moderator_user):
        """Moderator can access the reports list."""
        login(client, 'mod@example.com')
        resp = client.get('/moderation/reports')
        assert resp.status_code == 200

    def test_regular_user_cannot_access_report_detail(self, client, regular_user, admin_user, sample_listing, app):
        """Non-admin user gets 403 on report detail."""
        with app.app_context():
            report = Report(
                reporter_id=admin_user,
                target_type='listing',
                target_id=sample_listing,
                reason='spam',
            )
            db.session.add(report)
            db.session.commit()
            report_id = report.id

        login(client, 'test@example.com')
        resp = client.get(f'/moderation/reports/{report_id}')
        assert resp.status_code == 403


class TestAdminActions:
    def _create_report(self, app, reporter_id, listing_id):
        with app.app_context():
            report = Report(
                reporter_id=reporter_id,
                target_type='listing',
                target_id=listing_id,
                reason='spam',
            )
            db.session.add(report)
            db.session.commit()
            return report.id

    def test_takedown_listing(self, client, admin_user, regular_user, sample_listing, app):
        """Admin can take down a listing via report."""
        report_id = self._create_report(app, admin_user, sample_listing)
        login(client, 'admin@example.com')
        resp = client.post(f'/moderation/reports/{report_id}/takedown', data={
            'admin_note': 'Violates policy',
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            listing = db.session.get(Listing, sample_listing)
            assert listing.is_removed is True
            assert listing.is_active is False
            assert listing.removed_reason == 'Violates policy'

    def test_restore_listing(self, client, admin_user, regular_user, sample_listing, app):
        """Admin can restore a taken-down listing."""
        report_id = self._create_report(app, admin_user, sample_listing)
        login(client, 'admin@example.com')
        client.post(f'/moderation/reports/{report_id}/takedown', data={
            'admin_note': 'Testing',
        })
        resp = client.post(f'/moderation/reports/{report_id}/restore', follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            listing = db.session.get(Listing, sample_listing)
            assert listing.is_removed is False
            assert listing.is_active is True

    def test_ban_user(self, client, admin_user, regular_user, sample_listing, app):
        """Admin can ban the user behind a reported listing."""
        report_id = self._create_report(app, admin_user, sample_listing)
        login(client, 'admin@example.com')
        resp = client.post(f'/moderation/reports/{report_id}/ban-user', data={
            'admin_note': 'Repeated violations',
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            user = db.session.get(User, regular_user)
            assert user.is_active is False
            assert user.ban_reason == 'Repeated violations'

    def test_unban_user(self, client, admin_user, regular_user, sample_listing, app):
        """Admin can unban a previously banned user."""
        report_id = self._create_report(app, admin_user, sample_listing)
        login(client, 'admin@example.com')
        client.post(f'/moderation/reports/{report_id}/ban-user', data={
            'admin_note': 'Test ban',
        })
        resp = client.post(f'/moderation/reports/{report_id}/unban-user', follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            user = db.session.get(User, regular_user)
            assert user.is_active is True
            assert user.ban_reason is None

    def test_resolve_report(self, client, admin_user, regular_user, sample_listing, app):
        """Admin can mark a report as resolved."""
        report_id = self._create_report(app, admin_user, sample_listing)
        login(client, 'admin@example.com')
        resp = client.post(f'/moderation/reports/{report_id}/resolve', data={
            'action': 'resolved',
            'admin_note': 'Reviewed and actioned',
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            report = db.session.get(Report, report_id)
            assert report.status == 'resolved'
            assert report.handled_by_id == admin_user

    def test_dismiss_report(self, client, admin_user, regular_user, sample_listing, app):
        """Admin can dismiss a report."""
        report_id = self._create_report(app, admin_user, sample_listing)
        login(client, 'admin@example.com')
        resp = client.post(f'/moderation/reports/{report_id}/resolve', data={
            'action': 'dismissed',
            'admin_note': 'No violation found',
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            report = db.session.get(Report, report_id)
            assert report.status == 'dismissed'


class TestEnforcement:
    def test_removed_listing_not_in_browse(self, client, admin_user, regular_user, sample_listing, app):
        """Removed listings do not appear in the public browse page."""
        with app.app_context():
            listing = db.session.get(Listing, sample_listing)
            listing.is_removed = True
            listing.is_active = False
            db.session.commit()

        resp = client.get('/listings/')
        assert b'Test Textbook' not in resp.data

    def test_removed_listing_blocked_for_regular_user(self, client, admin_user, regular_user, sample_listing, app):
        """Regular user is redirected if they try to view a removed listing."""
        with app.app_context():
            listing = db.session.get(Listing, sample_listing)
            listing.is_removed = True
            listing.is_active = False
            db.session.commit()

        login(client, 'admin@example.com')
        resp = client.get(f'/listings/{sample_listing}')
        assert resp.status_code == 200  # admin can view

        client.get('/auth/logout')

        from werkzeug.security import generate_password_hash
        with app.app_context():
            user2 = User(
                username='user2', email='user2@example.com',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(user2)
            db.session.commit()

        login(client, 'user2@example.com')
        resp = client.get(f'/listings/{sample_listing}', follow_redirects=True)
        assert b'removed by moderation' in resp.data

    def test_banned_user_cannot_login(self, client, regular_user, app):
        """Banned user cannot log in."""
        with app.app_context():
            user = db.session.get(User, regular_user)
            user.is_active = False
            db.session.commit()

        resp = login(client, 'test@example.com')
        assert b'suspended' in resp.data

    def test_banned_user_cannot_create_listing(self, client, regular_user, admin_user, sample_listing, app):
        """A banned user cannot create listings (tested via fresh login attempt)."""
        with app.app_context():
            report = Report(
                reporter_id=admin_user,
                target_type='listing',
                target_id=sample_listing,
                reason='spam',
            )
            db.session.add(report)
            db.session.commit()
            report_id = report.id

        login(client, 'admin@example.com')
        client.post(f'/moderation/reports/{report_id}/ban-user', data={
            'admin_note': 'Test ban',
        })
        client.get('/auth/logout')

        resp = login(client, 'test@example.com')
        assert b'suspended' in resp.data

        resp = client.post('/listings/new', data={
            'title': 'New Item',
            'description': 'test',
            'price': '10.0',
            'category': 'books',
        }, follow_redirects=True)
        assert b'Log In' in resp.data
        with app.app_context():
            listing = Listing.query.filter_by(title='New Item').first()
            assert listing is None

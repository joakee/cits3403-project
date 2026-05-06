from datetime import datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort)
from flask_login import login_required, current_user
from app import db, socketio
from app.models import Report, Listing, User
from app.forms import ReportForm

bp = Blueprint('moderation', __name__, url_prefix='/moderation')


def admin_or_mod_required(f):
    """Decorator that requires admin or moderator role."""
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not (current_user.is_admin or current_user.is_moderator):
            abort(403)
        return f(*args, **kwargs)
    return decorated


@bp.route('/report/listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def report_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id == current_user.id:
        flash('You cannot report your own listing.', 'warning')
        return redirect(url_for('listings.detail', listing_id=listing_id))

    existing = Report.query.filter_by(
        reporter_id=current_user.id,
        target_type='listing',
        target_id=listing_id,
        status='open'
    ).first()
    if existing:
        flash('You already have an open report for this listing.', 'info')
        return redirect(url_for('listings.detail', listing_id=listing_id))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            target_type='listing',
            target_id=listing_id,
            reason=form.reason.data,
            description=form.description.data or None,
        )
        db.session.add(report)
        db.session.commit()
        flash('Report submitted. Our team will review it shortly.', 'success')
        return redirect(url_for('listings.detail', listing_id=listing_id))

    return render_template('moderation/report_form.html', form=form, listing=listing)


@bp.route('/report/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def report_user(user_id):
    target_user = User.query.get_or_404(user_id)

    if target_user.id == current_user.id:
        flash('You cannot report yourself.', 'warning')
        return redirect(url_for('profile.view', user_id=user_id))

    existing = Report.query.filter_by(
        reporter_id=current_user.id,
        target_type='user',
        target_id=user_id,
        status='open'
    ).first()
    if existing:
        flash('You already have an open report for this user.', 'info')
        return redirect(url_for('profile.view', user_id=user_id))

    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            target_type='user',
            target_id=user_id,
            reason=form.reason.data,
            description=form.description.data or None,
        )
        db.session.add(report)
        db.session.commit()
        flash('Report submitted. Our team will review it shortly.', 'success')
        return redirect(url_for('profile.view', user_id=user_id))

    return render_template('moderation/report_user_form.html', form=form, target_user=target_user)


# --- Admin/Moderator routes ---

@bp.route('/reports')
@admin_or_mod_required
def reports_list():
    status_filter = request.args.get('status', 'open')
    target_filter = request.args.get('target_type', '')

    query = Report.query

    if status_filter and status_filter in Report.STATUS_CHOICES:
        query = query.filter_by(status=status_filter)

    if target_filter in ('listing', 'user'):
        query = query.filter_by(target_type=target_filter)

    reports = query.order_by(Report.created_at.desc()).all()

    counts = {
        'open': Report.query.filter_by(status='open').count(),
        'under_review': Report.query.filter_by(status='under_review').count(),
        'resolved': Report.query.filter_by(status='resolved').count(),
        'dismissed': Report.query.filter_by(status='dismissed').count(),
    }

    return render_template(
        'moderation/reports_list.html',
        reports=reports,
        status_filter=status_filter,
        target_filter=target_filter,
        counts=counts,
    )


@bp.route('/reports/<int:report_id>')
@admin_or_mod_required
def report_detail(report_id):
    report = Report.query.get_or_404(report_id)
    target = report.target
    return render_template('moderation/report_detail.html', report=report, target=target)


@bp.route('/reports/<int:report_id>/resolve', methods=['POST'])
@admin_or_mod_required
def resolve_report(report_id):
    report = Report.query.get_or_404(report_id)
    action = request.form.get('action')
    admin_note = request.form.get('admin_note', '').strip()

    if action not in ('resolved', 'dismissed'):
        flash('Invalid action.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    report.status = action
    report.handled_by_id = current_user.id
    report.admin_note = admin_note or None
    report.updated_at = datetime.utcnow()
    db.session.commit()

    flash(f'Report #{report.id} marked as {action}.', 'success')
    return redirect(url_for('moderation.reports_list'))


@bp.route('/reports/<int:report_id>/takedown', methods=['POST'])
@admin_or_mod_required
def takedown_listing(report_id):
    report = Report.query.get_or_404(report_id)

    if report.target_type != 'listing':
        flash('This report is not for a listing.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    listing = Listing.query.get(report.target_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    reason = request.form.get('admin_note', '').strip()

    listing.is_active = False
    listing.is_removed = True
    listing.removed_at = datetime.utcnow()
    listing.removed_reason = reason or f'Taken down via report #{report.id}'
    listing.removed_by_id = current_user.id

    report.status = 'resolved'
    report.handled_by_id = current_user.id
    report.admin_note = reason or 'Listing taken down'
    report.updated_at = datetime.utcnow()

    db.session.commit()
    socketio.emit('listing_removed', {'listing_id': listing.id})
    flash(f'Listing "{listing.title}" has been taken down.', 'success')
    return redirect(url_for('moderation.reports_list'))


@bp.route('/reports/<int:report_id>/restore', methods=['POST'])
@admin_or_mod_required
def restore_listing(report_id):
    report = Report.query.get_or_404(report_id)

    if report.target_type != 'listing':
        flash('This report is not for a listing.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    listing = Listing.query.get(report.target_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    listing.is_active = True
    listing.is_removed = False
    listing.removed_at = None
    listing.removed_reason = None
    listing.removed_by_id = None

    db.session.commit()
    socketio.emit('listing_restored', {'listing_id': listing.id})
    flash(f'Listing "{listing.title}" has been restored.', 'success')
    return redirect(url_for('moderation.report_detail', report_id=report_id))


@bp.route('/reports/<int:report_id>/ban-user', methods=['POST'])
@admin_or_mod_required
def ban_user(report_id):
    report = Report.query.get_or_404(report_id)

    if report.target_type == 'listing':
        listing = Listing.query.get(report.target_id)
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('moderation.report_detail', report_id=report_id))
        user = listing.seller
    else:
        user = User.query.get(report.target_id)

    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    if user.is_admin:
        flash('Cannot ban an admin user.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    reason = request.form.get('admin_note', '').strip()

    user.is_active = False
    user.banned_at = datetime.utcnow()
    user.ban_reason = reason or f'Banned via report #{report.id}'

    affected_listing_ids = []
    for listing in user.listings:
        listing.is_active = False
        affected_listing_ids.append(listing.id)

    report.status = 'resolved'
    report.handled_by_id = current_user.id
    report.admin_note = reason or f'User {user.username} banned'
    report.updated_at = datetime.utcnow()

    db.session.commit()
    for lid in affected_listing_ids:
        socketio.emit('listing_removed', {'listing_id': lid})
    flash(f'User "{user.username}" has been banned.', 'warning')
    return redirect(url_for('moderation.reports_list'))


@bp.route('/reports/<int:report_id>/unban-user', methods=['POST'])
@admin_or_mod_required
def unban_user(report_id):
    report = Report.query.get_or_404(report_id)

    if report.target_type == 'listing':
        listing = Listing.query.get(report.target_id)
        user = listing.seller if listing else None
    else:
        user = User.query.get(report.target_id)

    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('moderation.report_detail', report_id=report_id))

    user.is_active = True
    user.banned_at = None
    user.ban_reason = None

    db.session.commit()
    flash(f'User "{user.username}" has been unbanned.', 'success')
    return redirect(url_for('moderation.report_detail', report_id=report_id))

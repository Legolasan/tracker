from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from app.database import db
from app.models.application import Application, ApplicationStatus

applications_bp = Blueprint('applications', __name__, url_prefix='/applications')


@applications_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    
    query = Application.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search:
        query = query.filter(
            db.or_(
                Application.company.ilike(f'%{search}%'),
                Application.role.ilike(f'%{search}%')
            )
        )
    
    applications = query.order_by(Application.updated_at.desc()).all()
    
    return render_template('applications/index.html', 
                         applications=applications,
                         status_choices=ApplicationStatus.choices(),
                         current_status=status_filter,
                         search=search)


@applications_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        company = request.form.get('company', '').strip()
        role = request.form.get('role', '').strip()
        status = request.form.get('status', ApplicationStatus.SAVED)
        url = request.form.get('url', '').strip()
        location = request.form.get('location', '').strip()
        salary_range = request.form.get('salary_range', '').strip()
        date_applied_str = request.form.get('date_applied', '')
        notes = request.form.get('notes', '').strip()
        
        if not company or not role:
            flash('Company and role are required.', 'error')
            return render_template('applications/form.html', 
                                 status_choices=ApplicationStatus.choices(),
                                 application=None)
        
        date_applied = None
        if date_applied_str:
            try:
                date_applied = date.fromisoformat(date_applied_str)
            except ValueError:
                pass
        
        application = Application(
            user_id=current_user.id,
            company=company,
            role=role,
            status=status,
            url=url or None,
            location=location or None,
            salary_range=salary_range or None,
            date_applied=date_applied,
            notes=notes or None
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash(f'Application for {role} at {company} added!', 'success')
        return redirect(url_for('applications.show', id=application.id))
    
    return render_template('applications/form.html', 
                         status_choices=ApplicationStatus.choices(),
                         application=None)


@applications_bp.route('/<int:id>')
@login_required
def show(id):
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('applications/show.html', application=application)


@applications_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        application.company = request.form.get('company', '').strip()
        application.role = request.form.get('role', '').strip()
        application.status = request.form.get('status', ApplicationStatus.SAVED)
        application.url = request.form.get('url', '').strip() or None
        application.location = request.form.get('location', '').strip() or None
        application.salary_range = request.form.get('salary_range', '').strip() or None
        application.notes = request.form.get('notes', '').strip() or None
        
        date_applied_str = request.form.get('date_applied', '')
        if date_applied_str:
            try:
                application.date_applied = date.fromisoformat(date_applied_str)
            except ValueError:
                pass
        else:
            application.date_applied = None
        
        if not application.company or not application.role:
            flash('Company and role are required.', 'error')
            return render_template('applications/form.html', 
                                 status_choices=ApplicationStatus.choices(),
                                 application=application)
        
        db.session.commit()
        flash('Application updated!', 'success')
        return redirect(url_for('applications.show', id=application.id))
    
    return render_template('applications/form.html', 
                         status_choices=ApplicationStatus.choices(),
                         application=application)


@applications_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    company = application.company
    role = application.role
    
    db.session.delete(application)
    db.session.commit()
    
    flash(f'Application for {role} at {company} deleted.', 'info')
    return redirect(url_for('applications.index'))


@applications_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    application = Application.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    new_status = request.form.get('status')
    
    if new_status in ApplicationStatus.all():
        application.status = new_status
        db.session.commit()
        flash(f'Status updated to {application.status_display}', 'success')
    
    return redirect(request.referrer or url_for('applications.show', id=id))


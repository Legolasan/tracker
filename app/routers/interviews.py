from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app.database import db
from app.models.application import Application
from app.models.interview import Interview, InterviewType, InterviewOutcome

interviews_bp = Blueprint('interviews', __name__, url_prefix='/interviews')


@interviews_bp.route('/new')
@login_required
def new():
    application_id = request.args.get('application_id', type=int)
    application = None
    
    if application_id:
        application = Application.query.filter_by(id=application_id, user_id=current_user.id).first_or_404()
    
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.company).all()
    
    return render_template('interviews/form.html',
                         interview=None,
                         application=application,
                         applications=applications,
                         type_choices=InterviewType.choices(),
                         outcome_choices=InterviewOutcome.choices())


@interviews_bp.route('/create', methods=['POST'])
@login_required
def create():
    application_id = request.form.get('application_id', type=int)
    application = Application.query.filter_by(id=application_id, user_id=current_user.id).first_or_404()
    
    interview_type = request.form.get('interview_type', InterviewType.OTHER)
    scheduled_date = request.form.get('scheduled_date', '')
    scheduled_time = request.form.get('scheduled_time', '')
    duration = request.form.get('duration_minutes', 60, type=int)
    interviewer = request.form.get('interviewer', '').strip()
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not scheduled_date or not scheduled_time:
        flash('Date and time are required.', 'error')
        return redirect(url_for('interviews.new', application_id=application_id))
    
    try:
        scheduled_at = datetime.strptime(f'{scheduled_date} {scheduled_time}', '%Y-%m-%d %H:%M')
    except ValueError:
        flash('Invalid date or time format.', 'error')
        return redirect(url_for('interviews.new', application_id=application_id))
    
    interview = Interview(
        application_id=application_id,
        interview_type=interview_type,
        scheduled_at=scheduled_at,
        duration_minutes=duration,
        interviewer=interviewer or None,
        location=location or None,
        notes=notes or None
    )
    
    db.session.add(interview)
    db.session.commit()
    
    flash(f'{interview.type_display} interview scheduled!', 'success')
    return redirect(url_for('applications.show', id=application_id))


@interviews_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    interview = Interview.query.join(Application).filter(
        Interview.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        interview.interview_type = request.form.get('interview_type', InterviewType.OTHER)
        scheduled_date = request.form.get('scheduled_date', '')
        scheduled_time = request.form.get('scheduled_time', '')
        interview.duration_minutes = request.form.get('duration_minutes', 60, type=int)
        interview.interviewer = request.form.get('interviewer', '').strip() or None
        interview.location = request.form.get('location', '').strip() or None
        interview.notes = request.form.get('notes', '').strip() or None
        interview.outcome = request.form.get('outcome', InterviewOutcome.PENDING)
        interview.feedback = request.form.get('feedback', '').strip() or None
        
        if scheduled_date and scheduled_time:
            try:
                interview.scheduled_at = datetime.strptime(f'{scheduled_date} {scheduled_time}', '%Y-%m-%d %H:%M')
            except ValueError:
                flash('Invalid date or time format.', 'error')
                return render_template('interviews/form.html',
                                     interview=interview,
                                     application=interview.application,
                                     applications=[],
                                     type_choices=InterviewType.choices(),
                                     outcome_choices=InterviewOutcome.choices())
        
        db.session.commit()
        flash('Interview updated!', 'success')
        return redirect(url_for('applications.show', id=interview.application_id))
    
    return render_template('interviews/form.html',
                         interview=interview,
                         application=interview.application,
                         applications=[],
                         type_choices=InterviewType.choices(),
                         outcome_choices=InterviewOutcome.choices())


@interviews_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    interview = Interview.query.join(Application).filter(
        Interview.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    application_id = interview.application_id
    db.session.delete(interview)
    db.session.commit()
    
    flash('Interview deleted.', 'info')
    return redirect(url_for('applications.show', id=application_id))


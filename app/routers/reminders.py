from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date, timedelta
from app.database import db
from app.models.application import Application
from app.models.reminder import Reminder

reminders_bp = Blueprint('reminders', __name__, url_prefix='/reminders')


@reminders_bp.route('/')
@login_required
def index():
    show_completed = request.args.get('completed', 'false') == 'true'
    
    query = Reminder.query.join(Application).filter(Application.user_id == current_user.id)
    
    if not show_completed:
        query = query.filter(Reminder.completed == False)
    
    reminders = query.order_by(Reminder.remind_on).all()
    
    # Group reminders
    overdue = [r for r in reminders if r.is_overdue]
    today = [r for r in reminders if r.remind_on == date.today() and not r.completed]
    upcoming = [r for r in reminders if r.remind_on > date.today() and not r.completed]
    completed = [r for r in reminders if r.completed] if show_completed else []
    
    return render_template('reminders/index.html',
                         overdue=overdue,
                         today=today,
                         upcoming=upcoming,
                         completed=completed,
                         show_completed=show_completed)


@reminders_bp.route('/new')
@login_required
def new():
    application_id = request.args.get('application_id', type=int)
    application = None
    
    if application_id:
        application = Application.query.filter_by(id=application_id, user_id=current_user.id).first_or_404()
    
    applications = Application.query.filter_by(user_id=current_user.id).order_by(Application.company).all()
    
    # Default to 1 week from now
    default_date = (date.today() + timedelta(days=7)).isoformat()
    
    return render_template('reminders/form.html',
                         reminder=None,
                         application=application,
                         applications=applications,
                         default_date=default_date)


@reminders_bp.route('/create', methods=['POST'])
@login_required
def create():
    application_id = request.form.get('application_id', type=int)
    application = Application.query.filter_by(id=application_id, user_id=current_user.id).first_or_404()
    
    message = request.form.get('message', '').strip()
    remind_on_str = request.form.get('remind_on', '')
    
    if not message:
        flash('Message is required.', 'error')
        return redirect(url_for('reminders.new', application_id=application_id))
    
    if not remind_on_str:
        flash('Date is required.', 'error')
        return redirect(url_for('reminders.new', application_id=application_id))
    
    try:
        remind_on = date.fromisoformat(remind_on_str)
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('reminders.new', application_id=application_id))
    
    reminder = Reminder(
        application_id=application_id,
        message=message,
        remind_on=remind_on
    )
    
    db.session.add(reminder)
    db.session.commit()
    
    flash('Reminder set!', 'success')
    return redirect(url_for('applications.show', id=application_id))


@reminders_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    reminder = Reminder.query.join(Application).filter(
        Reminder.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    if request.method == 'POST':
        reminder.message = request.form.get('message', '').strip()
        remind_on_str = request.form.get('remind_on', '')
        
        if not reminder.message:
            flash('Message is required.', 'error')
            return render_template('reminders/form.html',
                                 reminder=reminder,
                                 application=reminder.application,
                                 applications=[])
        
        if remind_on_str:
            try:
                reminder.remind_on = date.fromisoformat(remind_on_str)
            except ValueError:
                flash('Invalid date format.', 'error')
                return render_template('reminders/form.html',
                                     reminder=reminder,
                                     application=reminder.application,
                                     applications=[])
        
        db.session.commit()
        flash('Reminder updated!', 'success')
        return redirect(url_for('reminders.index'))
    
    return render_template('reminders/form.html',
                         reminder=reminder,
                         application=reminder.application,
                         applications=[])


@reminders_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete(id):
    reminder = Reminder.query.join(Application).filter(
        Reminder.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    reminder.completed = True
    db.session.commit()
    
    flash('Reminder marked as complete.', 'success')
    return redirect(request.referrer or url_for('reminders.index'))


@reminders_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    reminder = Reminder.query.join(Application).filter(
        Reminder.id == id,
        Application.user_id == current_user.id
    ).first_or_404()
    
    db.session.delete(reminder)
    db.session.commit()
    
    flash('Reminder deleted.', 'info')
    return redirect(request.referrer or url_for('reminders.index'))


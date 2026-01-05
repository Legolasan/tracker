from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from sqlalchemy import func
from app.database import db
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview, InterviewOutcome
from app.models.reminder import Reminder

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    # Get status counts
    status_counts = db.session.query(
        Application.status,
        func.count(Application.id)
    ).filter(
        Application.user_id == current_user.id
    ).group_by(Application.status).all()
    
    status_counts_dict = dict(status_counts)
    
    # Calculate totals
    total_applications = sum(status_counts_dict.values())
    active_count = sum(
        status_counts_dict.get(s, 0) 
        for s in [ApplicationStatus.APPLIED, ApplicationStatus.PHONE_SCREEN, 
                  ApplicationStatus.INTERVIEWING, ApplicationStatus.FINAL_ROUND]
    )
    offer_count = status_counts_dict.get(ApplicationStatus.OFFER, 0)
    rejected_count = status_counts_dict.get(ApplicationStatus.REJECTED, 0)
    
    # Get due reminders (today and overdue)
    due_reminders = Reminder.query.join(Application).filter(
        Application.user_id == current_user.id,
        Reminder.completed == False,
        Reminder.remind_on <= date.today()
    ).order_by(Reminder.remind_on).limit(5).all()
    
    # Get upcoming interviews (next 7 days)
    upcoming_interviews = Interview.query.join(Application).filter(
        Application.user_id == current_user.id,
        Interview.outcome == InterviewOutcome.PENDING,
        Interview.scheduled_at >= datetime.utcnow(),
        Interview.scheduled_at <= datetime.utcnow() + timedelta(days=7)
    ).order_by(Interview.scheduled_at).limit(5).all()
    
    # Get recent applications
    recent_applications = Application.query.filter_by(
        user_id=current_user.id
    ).order_by(Application.updated_at.desc()).limit(5).all()
    
    # Stats for display
    stats = [
        {'label': 'Total Applications', 'value': total_applications, 'color': 'primary', 'icon': 'fa-briefcase'},
        {'label': 'Active', 'value': active_count, 'color': 'blue', 'icon': 'fa-spinner'},
        {'label': 'Offers', 'value': offer_count, 'color': 'green', 'icon': 'fa-trophy'},
        {'label': 'Rejected', 'value': rejected_count, 'color': 'red', 'icon': 'fa-times-circle'},
    ]
    
    return render_template('dashboard.html',
                         stats=stats,
                         status_counts=status_counts_dict,
                         due_reminders=due_reminders,
                         upcoming_interviews=upcoming_interviews,
                         recent_applications=recent_applications,
                         ApplicationStatus=ApplicationStatus)


@dashboard_bp.route('/welcome')
def welcome():
    """Landing page for non-authenticated users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


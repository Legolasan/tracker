from datetime import datetime
from app.database import db


class InterviewType:
    PHONE_SCREEN = 'phone_screen'
    TECHNICAL = 'technical'
    BEHAVIORAL = 'behavioral'
    ONSITE = 'onsite'
    FINAL = 'final'
    HR = 'hr'
    OTHER = 'other'
    
    @classmethod
    def choices(cls):
        return [
            (cls.PHONE_SCREEN, 'Phone Screen'),
            (cls.TECHNICAL, 'Technical'),
            (cls.BEHAVIORAL, 'Behavioral'),
            (cls.ONSITE, 'Onsite'),
            (cls.FINAL, 'Final Round'),
            (cls.HR, 'HR'),
            (cls.OTHER, 'Other'),
        ]


class InterviewOutcome:
    PENDING = 'pending'
    PASSED = 'passed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    @classmethod
    def choices(cls):
        return [
            (cls.PENDING, 'Pending'),
            (cls.PASSED, 'Passed'),
            (cls.FAILED, 'Failed'),
            (cls.CANCELLED, 'Cancelled'),
        ]


class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    interview_type = db.Column(db.String(50), default=InterviewType.OTHER)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    interviewer = db.Column(db.String(200))
    location = db.Column(db.String(300))  # Can be link for virtual
    notes = db.Column(db.Text)
    outcome = db.Column(db.String(50), default=InterviewOutcome.PENDING)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def type_display(self):
        type_map = dict(InterviewType.choices())
        return type_map.get(self.interview_type, self.interview_type)
    
    @property
    def outcome_display(self):
        outcome_map = dict(InterviewOutcome.choices())
        return outcome_map.get(self.outcome, self.outcome)
    
    @property
    def is_upcoming(self):
        return self.scheduled_at > datetime.utcnow() and self.outcome == InterviewOutcome.PENDING
    
    def __repr__(self):
        return f'<Interview {self.interview_type} for Application {self.application_id}>'


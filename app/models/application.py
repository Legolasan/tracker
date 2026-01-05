from datetime import datetime
from app.database import db


class ApplicationStatus:
    SAVED = 'saved'
    APPLIED = 'applied'
    PHONE_SCREEN = 'phone_screen'
    INTERVIEWING = 'interviewing'
    FINAL_ROUND = 'final_round'
    OFFER = 'offer'
    REJECTED = 'rejected'
    WITHDRAWN = 'withdrawn'
    
    @classmethod
    def choices(cls):
        return [
            (cls.SAVED, 'Saved'),
            (cls.APPLIED, 'Applied'),
            (cls.PHONE_SCREEN, 'Phone Screen'),
            (cls.INTERVIEWING, 'Interviewing'),
            (cls.FINAL_ROUND, 'Final Round'),
            (cls.OFFER, 'Offer'),
            (cls.REJECTED, 'Rejected'),
            (cls.WITHDRAWN, 'Withdrawn'),
        ]
    
    @classmethod
    def all(cls):
        return [cls.SAVED, cls.APPLIED, cls.PHONE_SCREEN, cls.INTERVIEWING, 
                cls.FINAL_ROUND, cls.OFFER, cls.REJECTED, cls.WITHDRAWN]


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default=ApplicationStatus.SAVED, index=True)
    url = db.Column(db.String(500))
    location = db.Column(db.String(200))
    salary_range = db.Column(db.String(100))
    date_applied = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interviews = db.relationship('Interview', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='application', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def status_display(self):
        status_map = dict(ApplicationStatus.choices())
        return status_map.get(self.status, self.status)
    
    @property
    def status_color(self):
        colors = {
            ApplicationStatus.SAVED: 'gray',
            ApplicationStatus.APPLIED: 'blue',
            ApplicationStatus.PHONE_SCREEN: 'indigo',
            ApplicationStatus.INTERVIEWING: 'purple',
            ApplicationStatus.FINAL_ROUND: 'yellow',
            ApplicationStatus.OFFER: 'green',
            ApplicationStatus.REJECTED: 'red',
            ApplicationStatus.WITHDRAWN: 'gray',
        }
        return colors.get(self.status, 'gray')
    
    def __repr__(self):
        return f'<Application {self.company} - {self.role}>'


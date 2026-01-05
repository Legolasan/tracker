from datetime import datetime, date
from app.database import db


class Reminder(db.Model):
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    remind_on = db.Column(db.Date, nullable=False, index=True)
    message = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_due(self):
        return not self.completed and self.remind_on <= date.today()
    
    @property
    def is_overdue(self):
        return not self.completed and self.remind_on < date.today()
    
    @property
    def days_until(self):
        if self.completed:
            return None
        delta = self.remind_on - date.today()
        return delta.days
    
    def __repr__(self):
        return f'<Reminder {self.message[:20]} for Application {self.application_id}>'


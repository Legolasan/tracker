from datetime import datetime
from app.database import db


class DocumentType:
    RESUME = 'resume'
    COVER_LETTER = 'cover_letter'
    PORTFOLIO = 'portfolio'
    OTHER = 'other'
    
    @classmethod
    def choices(cls):
        return [
            (cls.RESUME, 'Resume'),
            (cls.COVER_LETTER, 'Cover Letter'),
            (cls.PORTFOLIO, 'Portfolio'),
            (cls.OTHER, 'Other'),
        ]


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False, index=True)
    document_type = db.Column(db.String(50), default=DocumentType.OTHER)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500))  # External link (Google Drive, Dropbox, etc.)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def type_display(self):
        type_map = dict(DocumentType.choices())
        return type_map.get(self.document_type, self.document_type)
    
    def __repr__(self):
        return f'<Document {self.filename} for Application {self.application_id}>'


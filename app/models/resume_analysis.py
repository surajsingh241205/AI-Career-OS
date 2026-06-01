from app import db
from datetime import datetime


class ResumeAnalysis(db.Model):

    __tablename__ = "resume_analysis"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    resume_id = db.Column(
        db.Integer,
        db.ForeignKey("resumes.id"),
        nullable=False
    )

    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    skills = db.Column(db.Text)

    score = db.Column(
    db.Integer,
    default=0
    )
    
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    
    
from app import db
from datetime import datetime


class JobApplication(db.Model):

    __tablename__ = "job_applications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    company_name = db.Column(
        db.String(200),
        nullable=False
    )

    job_title = db.Column(
        db.String(200),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Applied"
    )

    applied_date = db.Column(
        db.Date,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
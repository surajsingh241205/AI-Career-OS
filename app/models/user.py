from app import db
from datetime import datetime
from flask_login import UserMixin 

class User(UserMixin,db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    
    resumes = db.relationship(
        "Resume", backref = "user", lazy= True
    )
    
    applications = db.relationship(
    "JobApplication",
    backref="user",
    lazy=True,
    cascade="all, delete"
    )
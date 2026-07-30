from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from db import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    posts = db.relationship("Post", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)

    text = db.Column(db.Text, nullable=False)
    authority_response = db.Column(db.Text)

    status = db.Column(
        db.Enum(
            "Pending",
            "In Progress",
            "Resolved",
            "Rejected",
            name="report_status"
        ),
        nullable=False,
        default="Pending"
    )

    # GPS coordinates
    latitude = db.Column(db.Float, nullable=True)

    longitude = db.Column(db.Float, nullable=True)

    # Upvotes
    upvotes = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
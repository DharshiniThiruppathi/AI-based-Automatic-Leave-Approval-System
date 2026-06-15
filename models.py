from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # Possible roles: "student", "tutor", "academic coordinator", "hod"
    role = db.Column(db.String(50), nullable=False)  
    attendance_percentage = db.Column(db.Float, nullable=False, default=100.0)

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    # Possible statuses: "Submitted", "Tutor Approved", "Tutor Declined",
    # "Coordinator Approved", "Coordinator Declined", "HOD Approved", "HOD Declined"
    status = db.Column(db.String(50), nullable=False, default='Submitted')

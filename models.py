from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))  # ← ИЗМЕНИ 128 на 255
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(20), unique=True)  # номер студенческого
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    phone = db.Column(db.String(20))
    
    user = db.relationship('User', backref='student')
    group = db.relationship('Group', backref='students')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # ИТ-21
    course = db.Column(db.Integer)  # 1, 2, 3, 4 курс

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Integer)  # 2, 3, 4, 5
    date = db.Column(db.Date, default=datetime.utcnow)
    
    student = db.relationship('Student', backref='grades')
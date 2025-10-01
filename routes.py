from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, User, Student, Grade, Group
from werkzeug.security import generate_password_hash, check_password_hash

# Blueprints для организации маршрутов
auth_routes = Blueprint('auth', __name__)
student_routes = Blueprint('students', __name__)

# Аутентификация
@auth_routes.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'token': access_token,
            'user_id': user.id,
            'role': user.role
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

# Получить всех студентов
@student_routes.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.full_name,
        'student_id': s.student_id,
        'group': s.group.name if s.group else None
    } for s in students])

# Получить студента по ID
@student_routes.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'id': student.id,
        'name': student.full_name,
        'student_id': student.student_id,
        'group': student.group.name if student.group else None,
        'grades': [{
            'subject': g.subject,
            'grade': g.grade,
            'date': g.date.isoformat()
        } for g in student.grades]
    })

# Тестовый маршрут
@student_routes.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Backend работает!'})
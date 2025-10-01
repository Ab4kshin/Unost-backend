from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, User, Student, Grade, Group
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Правильное определение Blueprint
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

# Регистрация
@auth_routes.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Проверяем, что пользователь с таким email не существует
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
    
    # Создаем пользователя
    user = User(
        email=data.get('email'),
        role='student'
    )
    user.set_password(data.get('password'))
    
    db.session.add(user)
    db.session.flush()  # Получаем ID пользователя
    
    # Находим или создаем группу
    group_name = data.get('group')
    group = Group.query.filter_by(name=group_name).first()
    if not group:
        group = Group(name=group_name)
        db.session.add(group)
        db.session.flush()
    
    # Создаем студента
    student = Student(
        user_id=user.id,
        full_name=data.get('full_name'),
        phone=data.get('phone'),
        group_id=group.id
    )
    
    # Парсим дату рождения
    if data.get('birth_date'):
        try:
            student.birth_date = datetime.strptime(data.get('birth_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    db.session.add(student)
    db.session.commit()
    
    # Создаем токен
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'token': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'full_name': student.full_name,
            'group': group.name
        }
    }), 201

# Получить всех студентов
@student_routes.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    students = Student.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.full_name,
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
        'group': student.group.name if student.group else None,
        'grades': [{
            'subject': g.subject,
            'grade': g.grade,
            'date': g.date.isoformat()
        } for g in student.grades]
    })

# Получить профиль студента
@student_routes.route('/api/students/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first_or_404()
    
    return jsonify({
        'id': student.id,
        'full_name': student.full_name,
        'email': student.user.email,
        'phone': student.phone,
        'group': student.group.name if student.group else None
    })

# Тестовый маршрут
@student_routes.route('/api/test', methods=['GET'])
def test():
    return jsonify({'message': 'Backend работает!'})

# Получить профиль студента
@student_routes.route('/api/students/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first_or_404()
    
    return jsonify({
        'id': student.id,
        'full_name': student.full_name,
        'email': student.user.email,
        'phone': student.phone,
        'birth_date': student.birth_date.isoformat() if student.birth_date else None,
        'group': student.group.name if student.group else None,
        'group_id': student.group_id,
        'user_id': student.user_id
    })

# Добавьте этот маршрут в конец файла routes.py

# Корневой маршрут
@auth_routes.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'UNOST Backend is running!', 
        'status': 'OK',
        'endpoints': {
            'login': '/api/login',
            'register': '/api/register',
            'students': '/api/students',
            'test': '/api/test'
        }
    })

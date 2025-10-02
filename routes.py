from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models import db, User, Student, Grade, Group
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_routes = Blueprint('auth', __name__)
student_routes = Blueprint('students', __name__)

# Аутентификация
@auth_routes.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print("Login attempt:", data.get('email'))
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email и пароль обязательны'}), 400
            
        user = User.query.filter_by(email=data.get('email')).first()
        
        if user and check_password_hash(user.password_hash, data.get('password')):
            # ИСПРАВЛЕНИЕ: преобразуем user.id в строку
            access_token = create_access_token(identity=str(user.id))
            print(f"Login successful for user {user.id}, token created")
            return jsonify({
                'token': access_token,
                'user_id': user.id,
                'role': user.role
            })
        
        print("Login failed: invalid credentials")
        return jsonify({'error': 'Неверные учетные данные'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

# Регистрация
@auth_routes.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("Registration attempt:", data.get('email'))  # Отладка
        
        # Валидация обязательных полей
        required_fields = ['email', 'password', 'full_name', 'phone', 'birth_date', 'group']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Поле {field} обязательно'}), 400
        
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
        db.session.flush()
        print(f"User created with ID: {user.id}")  # Отладка
    
        # Находим или создаем группу
        group_name = data.get('group')
        group = Group.query.filter_by(name=group_name).first()
        if not group:
            group = Group(name=group_name)
            db.session.add(group)
            db.session.flush()
            print(f"Group created: {group_name}")  # Отладка
        
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
                return jsonify({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}), 400
        
        db.session.add(student)
        db.session.commit()
        
        # Создаем токен - ИСПРАВЛЕНИЕ: преобразуем user.id в строку
        access_token = create_access_token(identity=str(user.id))
        print(f"Registration successful, token created for user {user.id}")  # Отладка
        
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
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")  # Отладка
        return jsonify({'error': f'Ошибка регистрации: {str(e)}'}), 500

# Получить профиль студента
@student_routes.route('/api/students/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        print(f"Profile request for user_id: {user_id}")  # Отладка
        
        # ИСПРАВЛЕНИЕ: преобразуем строку обратно в int для поиска в базе
        student = Student.query.filter_by(user_id=int(user_id)).first()
        
        if not student:
            print(f"Student not found for user_id: {user_id}")  # Отладка
            return jsonify({'error': 'Профиль студента не найден'}), 404
        
        print(f"Profile found for: {student.full_name}")  # Отладка
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
    except Exception as e:
        print(f"Profile error: {str(e)}")  # Отладка
        return jsonify({'error': f'Ошибка загрузки профиля: {str(e)}'}), 500

# Тестовый маршрут для проверки JWT
@auth_routes.route('/api/check-token', methods=['GET'])
@jwt_required()
def check_token():
    user_id = get_jwt_identity()
    return jsonify({'message': 'Token is valid', 'user_id': user_id})

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
            'test': '/api/test',
            'check-token': '/api/check-token'
        }
    })

# Эндпоинт для отладки JWT - проверяет токен без требований к базе
@auth_routes.route('/api/debug-token', methods=['POST'])
def debug_token():
    try:
        data = request.get_json()
        token = data.get('token')
        print(f"🔐 Отладка токена: {token}")
        
        if not token:
            return jsonify({'error': 'Токен не предоставлен'}), 400
        
        # Пытаемся декодировать токен
        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(token)
            print(f"✅ Токен декодирован: {decoded}")
            return jsonify({
                'status': 'valid',
                'decoded': decoded
            }), 200
        except Exception as e:
            print(f"❌ Ошибка декодирования: {str(e)}")
            return jsonify({
                'status': 'invalid',
                'error': str(e)
            }), 422
            
    except Exception as e:
        return jsonify({'error': f'Ошибка отладки: {str(e)}'}), 500
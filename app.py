from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация с абсолютным путем
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(basedir, 'instance', 'unost.db')
    
    # Улучшенная конфигурация JWT
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SECRET_KEY'] = 'super-secret-key-12345-fixed'  # ФИКСИРОВАННЫЙ КЛЮЧ
    app.config['JWT_SECRET_KEY'] = 'jwt-super-secret-key-67890-fixed'  # ФИКСИРОВАННЫЙ КЛЮЧ
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Токены не истекают
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Явно указываем где искать токен
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print("=== КОНФИГУРАЦИЯ JWT ===")
    print(f"JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY']}")
    print(f"SECRET_KEY: {app.config['SECRET_KEY']}")
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # CORS настройки
    CORS(app, 
         origins=["http://localhost:5173", "http://127.0.0.1:5173"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Headers"],
         supports_credentials=True)
    
    # Регистрация маршрутов
    from routes import auth_routes, student_routes
    app.register_blueprint(auth_routes)
    app.register_blueprint(student_routes)
    
    return app

app = create_app()

with app.app_context():
    from models import User, Student, Group, Grade
    db.create_all()
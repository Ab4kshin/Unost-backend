from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv  # ← ДОБАВЬ ЭТУ СТРОКУ

# ЗАГРУЗКА ПЕРЕМЕННЫХ ИЗ .env ФАЙЛА
load_dotenv()  # ← ДОБАВЬ ЭТУ СТРОКУ

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])  # Vue dev server

    # Конфигурация из .env файла
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)  # Разрешаем запросы от фронтенда
    
    # Регистрация маршрутов
    from routes import auth_routes, student_routes
    app.register_blueprint(auth_routes)
    app.register_blueprint(student_routes)
    
    return app

# Создаем приложение
app = create_app()
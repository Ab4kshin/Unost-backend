from app import app, db
from models import User  # Добавь этот импорт

if __name__ == '__main__':
    with app.app_context():
        # Создаем таблицы в базе данных
        db.create_all()
        
        # Создаем тестового пользователя если его нет
        if not User.query.filter_by(email='admin@college.ru').first():
            admin = User(email='admin@college.ru', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Создан тестовый пользователь: admin@college.ru / admin123')
    
    # Запускаем сервер
    app.run(debug=True, port=5000)
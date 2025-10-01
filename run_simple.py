from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models import User

if __name__ == '__main__':
    with app.app_context():
        # УДАЛИМ и пересоздадим все таблицы
        db.drop_all()
        db.create_all()
        
        # Создаем тестового пользователя
        admin = User(email='admin@college.ru', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print('✅ База пересоздана!')
        print('👤 Тестовый пользователь: admin@college.ru / admin123')
        print('🚀 Сервер запускается...')
    
    app.run(debug=True, port=5000)
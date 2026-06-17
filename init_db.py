from app import app, db
from models import Teacher, SystemSettings
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Create super admin
    admin = Teacher.query.filter_by(username='admin').first()
    if not admin:
        admin = Teacher(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        print('✅ Default admin created: admin / admin123')
    else:
        print('✅ Admin already exists')
    
    # Create default settings
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings(voting_open=False)
        db.session.add(settings)
        print('✅ Default settings created')
    else:
        print('✅ Settings already exist')
    
    db.session.commit()
    print('✅ Database initialized successfully!')
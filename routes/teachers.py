from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, Teacher
from utils.decorators import admin_required
from datetime import datetime

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/api/teachers', methods=['GET'])
@admin_required
def get_teacher(teacher):
    teacher_account = Teacher.query.filter_by(is_admin=False).first()
    if not teacher_account:
        return jsonify({'teacher': None})
    
    return jsonify({
        'teacher': {
            'id': teacher_account.id,
            'username': teacher_account.username,
            'updated_at': teacher_account.updated_at.isoformat()
        }
    })

@teachers_bp.route('/api/teachers/credentials', methods=['PUT'])
@admin_required
def update_teacher_credentials(teacher):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    teacher_account = Teacher.query.filter_by(is_admin=False).first()
    
    if teacher_account:
        teacher_account.username = username
        teacher_account.password_hash = generate_password_hash(password)
        teacher_account.updated_at = datetime.utcnow()
    else:
        teacher_account = Teacher(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        db.session.add(teacher_account)

    db.session.commit()
    return jsonify({'message': 'Teacher credentials updated'})
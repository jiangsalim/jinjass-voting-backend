from flask import Blueprint, request, jsonify
from flask_login import login_required
from werkzeug.security import generate_password_hash
from models import db, Teacher
from utils.decorators import admin_required
from datetime import datetime

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/api/teachers', methods=['GET'])
@login_required
@admin_required
def get_teacher():
    teacher = Teacher.query.filter_by(is_admin=False).first()
    if not teacher:
        return jsonify({'teacher': None})
    
    return jsonify({
        'teacher': {
            'id': teacher.id,
            'username': teacher.username,
            'updated_at': teacher.updated_at.isoformat()
        }
    })

@teachers_bp.route('/api/teachers/credentials', methods=['PUT'])
@login_required
@admin_required
def update_teacher_credentials():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    teacher = Teacher.query.filter_by(is_admin=False).first()
    
    if teacher:
        teacher.username = username
        teacher.password_hash = generate_password_hash(password)
        teacher.updated_at = datetime.utcnow()
    else:
        teacher = Teacher(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        db.session.add(teacher)

    db.session.commit()
    return jsonify({'message': 'Teacher credentials updated'})
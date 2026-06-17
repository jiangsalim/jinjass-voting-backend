from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models import db, Teacher, SystemSettings
from utils.token_utils import create_token, verify_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    teacher = Teacher.query.filter_by(username=username).first()

    if not teacher or not check_password_hash(teacher.password_hash, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    if not teacher.is_admin:
        settings = SystemSettings.query.first()
        if settings and not settings.voting_open:
            return jsonify({'error': 'Voting is currently closed. Please contact the administrator.'}), 403

    token = create_token(teacher.id, teacher.is_admin)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': teacher.id,
            'username': teacher.username,
            'is_admin': teacher.is_admin
        }
    })

@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    teacher = Teacher.query.get(payload['teacher_id'])
    if not teacher:
        return jsonify({'error': 'User not found'}), 401
    
    return jsonify({
        'user': {
            'id': teacher.id,
            'username': teacher.username,
            'is_admin': teacher.is_admin
        }
    })
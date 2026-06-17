from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, Teacher, SystemSettings

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

    # Check if voting is closed for non-admin
    if not teacher.is_admin:
        settings = SystemSettings.query.first()
        if settings and not settings.voting_open:
            return jsonify({'error': 'Voting is currently closed. Please contact the administrator.'}), 403

    login_user(teacher)
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': teacher.id,
            'username': teacher.username,
            'is_admin': teacher.is_admin
        }
    })

@auth_bp.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        }
    })
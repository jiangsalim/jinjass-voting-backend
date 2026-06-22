from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Teacher
from utils.decorators import admin_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/admin/profile', methods=['GET'])
@admin_required
def get_profile(teacher):
    return jsonify({
        'profile': {
            'id': teacher.id,
            'username': teacher.username,
            'is_admin': teacher.is_admin
        }
    })

@profile_bp.route('/api/admin/profile', methods=['PUT'])
@admin_required
def update_profile(teacher):
    data = request.get_json()
    new_username = data.get('username')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    # Update username if provided
    if new_username and new_username != teacher.username:
        # Check if username already taken
        existing = Teacher.query.filter_by(username=new_username).first()
        if existing and existing.id != teacher.id:
            return jsonify({'error': 'Username already taken'}), 400
        teacher.username = new_username

    # Update password if provided
    if new_password:
        if not current_password:
            return jsonify({'error': 'Current password is required to change password'}), 400
        
        if not check_password_hash(teacher.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters'}), 400
        
        teacher.password_hash = generate_password_hash(new_password)

    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'id': teacher.id,
            'username': teacher.username,
            'is_admin': teacher.is_admin
        }
    })
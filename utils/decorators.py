from functools import wraps
from flask import request, jsonify
from routes.auth import verify_token
from models import Teacher, SystemSettings

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        teacher = Teacher.query.get(payload['teacher_id'])
        if not teacher:
            return jsonify({'error': 'User not found'}), 401
        
        return f(teacher, *args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if not payload.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        
        teacher = Teacher.query.get(payload['teacher_id'])
        return f(teacher, *args, **kwargs)
    return decorated_function

def voting_open_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        settings = SystemSettings.query.first()
        if not settings or not settings.voting_open:
            return jsonify({'error': 'Voting is currently closed'}), 403
        return f(*args, **kwargs)
    return decorated_function
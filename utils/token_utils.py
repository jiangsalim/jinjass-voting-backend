import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_token(teacher_id, is_admin):
    payload = {
        'teacher_id': teacher_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
        return payload
    except:
        return None
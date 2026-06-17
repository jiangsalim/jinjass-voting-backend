from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Stream, Class
from utils.decorators import admin_required

streams_bp = Blueprint('streams', __name__)

@streams_bp.route('/api/streams', methods=['GET'])
@login_required
def get_streams():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id is required'}), 400

    streams = Stream.query.filter_by(class_id=class_id).all()
    return jsonify({
        'streams': [{
            'id': s.id,
            'name': s.name,
            'class_id': s.class_id,
            'total_students': s.total_students
        } for s in streams]
    })

@streams_bp.route('/api/streams', methods=['POST'])
@login_required
@admin_required
def create_stream():
    data = request.get_json()
    name = data.get('name')
    class_id = data.get('class_id')
    total_students = data.get('total_students')

    if not name or not class_id or not total_students:
        return jsonify({'error': 'Name, class_id, and total_students are required'}), 400

    stream = Stream(name=name, class_id=class_id, total_students=total_students)
    db.session.add(stream)
    db.session.commit()

    return jsonify({
        'message': 'Stream created',
        'stream': {
            'id': stream.id,
            'name': stream.name,
            'class_id': stream.class_id,
            'total_students': stream.total_students
        }
    }), 201

@streams_bp.route('/api/streams/<int:stream_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_stream(stream_id):
    stream = Stream.query.get_or_404(stream_id)
    db.session.delete(stream)
    db.session.commit()
    return jsonify({'message': 'Stream deleted'})
from flask import Blueprint, request, jsonify
from models import db, Class
from utils.decorators import token_required, admin_required

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/api/classes', methods=['GET'])
@token_required
def get_classes(teacher):
    election_id = request.args.get('election_id')
    if not election_id:
        return jsonify({'error': 'election_id is required'}), 400

    classes = Class.query.filter_by(election_id=election_id).all()
    return jsonify({
        'classes': [{'id': c.id, 'name': c.name, 'election_id': c.election_id} for c in classes]
    })

@classes_bp.route('/api/classes', methods=['POST'])
@admin_required
def create_class(teacher):
    data = request.get_json()
    name = data.get('name')
    election_id = data.get('election_id')

    if not name or not election_id:
        return jsonify({'error': 'Name and election_id are required'}), 400

    class_obj = Class(name=name, election_id=election_id)
    db.session.add(class_obj)
    db.session.commit()

    return jsonify({
        'message': 'Class created',
        'class': {'id': class_obj.id, 'name': class_obj.name, 'election_id': class_obj.election_id}
    }), 201

@classes_bp.route('/api/classes/<int:class_id>', methods=['DELETE'])
@admin_required
def delete_class(teacher, class_id):
    class_obj = Class.query.get_or_404(class_id)
    db.session.delete(class_obj)
    db.session.commit()
    return jsonify({'message': 'Class deleted'})
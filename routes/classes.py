from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Class, Election
from utils.decorators import admin_required

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    election_id = request.args.get('election_id')
    if not election_id:
        return jsonify({'error': 'election_id is required'}), 400

    classes = Class.query.filter_by(election_id=election_id).all()
    return jsonify({
        'classes': [{
            'id': c.id,
            'name': c.name,
            'election_id': c.election_id
        } for c in classes]
    })

@classes_bp.route('/api/classes', methods=['POST'])
@login_required
@admin_required
def create_class():
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
        'class': {
            'id': class_obj.id,
            'name': class_obj.name,
            'election_id': class_obj.election_id
        }
    }), 201

@classes_bp.route('/api/classes/<int:class_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    db.session.delete(class_obj)
    db.session.commit()
    return jsonify({'message': 'Class deleted'})
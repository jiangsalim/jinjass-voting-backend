from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Candidate
from utils.decorators import admin_required

candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route('/api/candidates', methods=['GET'])
@login_required
def get_candidates():
    position_id = request.args.get('position_id')
    if not position_id:
        return jsonify({'error': 'position_id is required'}), 400

    candidates = Candidate.query.filter_by(position_id=position_id).all()
    return jsonify({
        'candidates': [{
            'id': c.id,
            'name': c.name,
            'position_id': c.position_id
        } for c in candidates]
    })

@candidates_bp.route('/api/candidates', methods=['POST'])
@login_required
@admin_required
def create_candidate():
    data = request.get_json()
    name = data.get('name')
    position_id = data.get('position_id')

    if not name or not position_id:
        return jsonify({'error': 'Name and position_id are required'}), 400

    candidate = Candidate(name=name, position_id=position_id)
    db.session.add(candidate)
    db.session.commit()

    return jsonify({
        'message': 'Candidate created',
        'candidate': {
            'id': candidate.id,
            'name': candidate.name,
            'position_id': candidate.position_id
        }
    }), 201

@candidates_bp.route('/api/candidates/<int:candidate_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    db.session.delete(candidate)
    db.session.commit()
    return jsonify({'message': 'Candidate deleted'})
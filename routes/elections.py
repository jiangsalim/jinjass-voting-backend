from flask import Blueprint, request, jsonify
from models import db, Election
from utils.decorators import token_required, admin_required
from datetime import datetime

elections_bp = Blueprint('elections', __name__)

@elections_bp.route('/api/elections', methods=['GET'])
@token_required
def get_elections(teacher):
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return jsonify({
        'elections': [{
            'id': e.id,
            'title': e.title,
            'year': e.year,
            'status': e.status,
            'created_at': e.created_at.isoformat(),
            'closed_at': e.closed_at.isoformat() if e.closed_at else None
        } for e in elections]
    })

@elections_bp.route('/api/elections', methods=['POST'])
@admin_required
def create_election(teacher):
    data = request.get_json()
    title = data.get('title')
    year = data.get('year')

    if not title or not year:
        return jsonify({'error': 'Title and year are required'}), 400

    election = Election(title=title, year=year)
    db.session.add(election)
    db.session.commit()

    return jsonify({
        'message': 'Election created',
        'election': {'id': election.id, 'title': election.title, 'year': election.year, 'status': election.status}
    }), 201

@elections_bp.route('/api/elections/<int:election_id>', methods=['PUT'])
@admin_required
def update_election(teacher, election_id):
    election = Election.query.get_or_404(election_id)
    data = request.get_json()

    if 'title' in data:
        election.title = data['title']
    if 'year' in data:
        election.year = data['year']
    if 'status' in data:
        election.status = data['status']
        if data['status'] == 'closed':
            election.closed_at = datetime.utcnow()
        elif data['status'] == 'active':
            election.closed_at = None

    db.session.commit()
    return jsonify({'message': 'Election updated'})

@elections_bp.route('/api/elections/<int:election_id>', methods=['DELETE'])
@admin_required
def delete_election(teacher, election_id):
    election = Election.query.get_or_404(election_id)
    db.session.delete(election)
    db.session.commit()
    return jsonify({'message': 'Election deleted'})
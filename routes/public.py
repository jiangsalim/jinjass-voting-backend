from flask import Blueprint, jsonify
from models import SystemSettings, Election, Position
from utils.vote_utils import calculate_winners

public_bp = Blueprint('public', __name__)

@public_bp.route('/api/public/results', methods=['GET'])
def public_results():
    settings = SystemSettings.query.first()
    
    if not settings or not settings.current_election_id:
        return jsonify({
            'status': 'no_election',
            'message': 'No active election',
            'results': None
        })

    election = Election.query.get(settings.current_election_id)
    if not election:
        return jsonify({
            'status': 'no_election',
            'message': 'Election not found',
            'results': None
        })

    results = calculate_winners(election.id)

    return jsonify({
        'status': election.status,
        'voting_open': settings.voting_open,
        'display_type': settings.display_type,
        'election': {
            'id': election.id,
            'title': election.title,
            'year': election.year
        },
        'results': results
    })
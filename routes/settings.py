from flask import Blueprint, request, jsonify
from models import db, SystemSettings, Election
from utils.decorators import token_required, admin_required
from datetime import datetime

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/settings', methods=['GET'])
@token_required
def get_settings(teacher):
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings(voting_open=False)
        db.session.add(settings)
        db.session.commit()

    current_election = None
    if settings.current_election_id:
        election = Election.query.get(settings.current_election_id)
        if election:
            current_election = {
                'id': election.id,
                'title': election.title,
                'year': election.year
            }

    return jsonify({
        'voting_open': settings.voting_open,
        'display_type': settings.display_type,
        'current_election': current_election
    })

@settings_bp.route('/api/settings/toggle-voting', methods=['POST'])
@admin_required
def toggle_voting(teacher):
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings(voting_open=False)
        db.session.add(settings)
        db.session.flush()

    settings.voting_open = not settings.voting_open

    if not settings.voting_open and settings.current_election_id:
        election = Election.query.get(settings.current_election_id)
        if election and election.status == 'active':
            election.status = 'closed'
            election.closed_at = datetime.utcnow()
    
    if settings.voting_open and settings.current_election_id:
        election = Election.query.get(settings.current_election_id)
        if election:
            election.status = 'active'
            election.closed_at = None

    db.session.commit()

    return jsonify({
        'voting_open': settings.voting_open,
        'message': 'Voting closed - results finalized' if not settings.voting_open else 'Voting opened'
    })

@settings_bp.route('/api/settings/display-type', methods=['PUT'])
@admin_required
def update_display_type(teacher):
    data = request.get_json()
    display_type = data.get('display_type')

    if display_type not in ['graphs', 'counts']:
        return jsonify({'error': 'display_type must be "graphs" or "counts"'}), 400

    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)

    settings.display_type = display_type
    db.session.commit()

    return jsonify({'message': 'Display type updated', 'display_type': display_type})

@settings_bp.route('/api/settings/current-election', methods=['PUT'])
@admin_required
def set_current_election(teacher):
    data = request.get_json()
    election_id = data.get('election_id')

    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)

    if settings.current_election_id:
        old_election = Election.query.get(settings.current_election_id)
        if old_election:
            old_election.status = 'closed'

    settings.current_election_id = election_id
    if election_id:
        election = Election.query.get(election_id)
        if election:
            election.status = 'active'
    
    db.session.commit()

    return jsonify({'message': 'Current election set'})
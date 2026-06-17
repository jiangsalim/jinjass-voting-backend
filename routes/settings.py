from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, SystemSettings, Election
from utils.decorators import admin_required
from datetime import datetime
from utils.vote_utils import calculate_winners

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
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
@login_required
@admin_required
def toggle_voting():
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings(voting_open=False)
        db.session.add(settings)
        db.session.flush()

    settings.voting_open = not settings.voting_open

    # If closing voting, mark election as closed
    if not settings.voting_open and settings.current_election_id:
        election = Election.query.get(settings.current_election_id)
        if election and election.status == 'active':
            election.status = 'closed'
            election.closed_at = datetime.utcnow()
    
    # If opening voting, mark election as active
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
@login_required
@admin_required
def update_display_type():
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
@login_required
@admin_required
def set_current_election():
    data = request.get_json()
    election_id = data.get('election_id')

    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)

    # Reset old active election
    if settings.current_election_id:
        old_election = Election.query.get(settings.current_election_id)
        if old_election:
            old_election.status = 'closed'

    # Set new active election
    settings.current_election_id = election_id
    if election_id:
        election = Election.query.get(election_id)
        if election:
            election.status = 'active'
    
    db.session.commit()

    return jsonify({'message': 'Current election set'})
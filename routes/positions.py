from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import db, Position
from utils.decorators import admin_required

positions_bp = Blueprint('positions', __name__)

@positions_bp.route('/api/positions', methods=['GET'])
@login_required
def get_positions():
    election_id = request.args.get('election_id')
    if not election_id:
        return jsonify({'error': 'election_id is required'}), 400

    positions = Position.query.filter_by(election_id=election_id).all()
    return jsonify({
        'positions': [{
            'id': p.id,
            'title': p.title,
            'election_id': p.election_id
        } for p in positions]
    })

@positions_bp.route('/api/positions', methods=['POST'])
@login_required
@admin_required
def create_position():
    data = request.get_json()
    title = data.get('title')
    election_id = data.get('election_id')

    if not title or not election_id:
        return jsonify({'error': 'Title and election_id are required'}), 400

    position = Position(title=title, election_id=election_id)
    db.session.add(position)
    db.session.commit()

    return jsonify({
        'message': 'Position created',
        'position': {
            'id': position.id,
            'title': position.title,
            'election_id': position.election_id
        }
    }), 201

@positions_bp.route('/api/positions/<int:position_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_position(position_id):
    position = Position.query.get_or_404(position_id)
    db.session.delete(position)
    db.session.commit()
    return jsonify({'message': 'Position deleted'})
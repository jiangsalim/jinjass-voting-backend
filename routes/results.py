from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required
from models import db, Election, VoteSubmission, VoteTally, Candidate, Position, SystemSettings
from utils.decorators import admin_required
from utils.vote_utils import calculate_winners
from utils.exports import export_excel, export_pdf
import io
from datetime import datetime

results_bp = Blueprint('results', __name__)

@results_bp.route('/api/results', methods=['GET'])
@login_required
@admin_required
def get_results():
    election_id = request.args.get('election_id')
    if not election_id:
        return jsonify({'error': 'election_id is required'}), 400

    election = Election.query.get_or_404(election_id)
    results = calculate_winners(election_id)

    return jsonify({
        'election': {
            'id': election.id,
            'title': election.title,
            'year': election.year,
            'status': election.status
        },
        'results': results
    })

@results_bp.route('/api/results/export', methods=['GET'])
@login_required
@admin_required
def export_results():
    election_id = request.args.get('election_id')
    format_type = request.args.get('format', 'excel')  # 'excel' or 'pdf'

    if not election_id:
        return jsonify({'error': 'election_id is required'}), 400

    election = Election.query.get_or_404(election_id)
    results = calculate_winners(election_id)

    title = f"{election.title} ({election.year})"

    if format_type == 'pdf':
        buffer = export_pdf(title, results)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'results_{election.year}.pdf'
        )
    else:
        buffer = export_excel(title, results)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'results_{election.year}.xlsx'
        )
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Stream, VoteSubmission, VoteTally, Class
from utils.decorators import voting_open_required
from utils.vote_utils import validate_votes, create_notification

votes_bp = Blueprint('votes', __name__)

@votes_bp.route('/api/votes/available-streams', methods=['GET'])
@login_required
@voting_open_required
def get_available_streams():
    class_id = request.args.get('class_id')
    if not class_id:
        return jsonify({'error': 'class_id is required'}), 400

    # Get all submitted stream IDs
    submitted_ids = [s.stream_id for s in VoteSubmission.query.all()]
    
    # Get streams for this class that are NOT submitted
    available = Stream.query.filter_by(class_id=class_id)\
                            .filter(~Stream.id.in_(submitted_ids if submitted_ids else [0]))\
                            .all()

    return jsonify({
        'streams': [{
            'id': s.id,
            'name': s.name,
            'total_students': s.total_students,
            'class_name': s.class_ref.name
        } for s in available]
    })

@votes_bp.route('/api/votes/submit', methods=['POST'])
@login_required
@voting_open_required
def submit_votes():
    if current_user.is_admin:
        return jsonify({'error': 'Admin cannot submit votes'}), 403

    data = request.get_json()
    stream_id = data.get('stream_id')
    votes = data.get('votes')  # { candidate_id: vote_count, ... }

    if not stream_id or not votes:
        return jsonify({'error': 'stream_id and votes are required'}), 400

    # Check if stream already submitted
    existing = VoteSubmission.query.filter_by(stream_id=stream_id).first()
    if existing:
        return jsonify({'error': 'Votes already submitted for this stream'}), 400

    stream = Stream.query.get_or_404(stream_id)

    # Validate votes (total per position must not exceed student count)
    is_valid, problem_position, attempted_total = validate_votes(stream, votes)
    if not is_valid:
        create_notification(stream, problem_position, attempted_total)
        return jsonify({
            'error': f'Total votes for {problem_position} exceed the number of students in this stream. '
                     f'Entered: {attempted_total}, Maximum allowed: {stream.total_students}'
        }), 400

    # Create submission
    submission = VoteSubmission(
        stream_id=stream_id,
        teacher_id=current_user.id
    )
    db.session.add(submission)
    db.session.flush()

    # Save tallies
    for candidate_id, vote_count in votes.items():
        tally = VoteTally(
            submission_id=submission.id,
            candidate_id=int(candidate_id),
            vote_count=int(vote_count or 0)
        )
        db.session.add(tally)

    db.session.commit()

    return jsonify({
        'message': 'Votes submitted successfully',
        'submission': {
            'id': submission.id,
            'stream_name': stream.name,
            'class_name': stream.class_ref.name,
            'submitted_at': submission.submitted_at.isoformat()
        }
    }), 201

@votes_bp.route('/api/votes/submissions', methods=['GET'])
@login_required
def get_submissions():
    submissions = VoteSubmission.query.order_by(VoteSubmission.submitted_at.desc()).all()
    result = []
    for s in submissions:
        stream = s.stream_ref
        class_obj = stream.class_ref if stream else None
        result.append({
            'id': s.id,
            'stream_id': s.stream_id,
            'stream_name': stream.name if stream else 'Unknown',
            'class_name': class_obj.name if class_obj else 'Unknown',
            'teacher_username': s.teacher.username if s.teacher else 'Unknown',
            'submitted_at': s.submitted_at.isoformat()
        })
    return jsonify({'submissions': result})
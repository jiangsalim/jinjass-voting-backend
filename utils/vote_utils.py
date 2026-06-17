from models import db, VoteSubmission, VoteTally, Candidate, Position, Notification

def validate_votes(stream, votes_data):
    """
    votes_data: { candidate_id: vote_count, ... }
    Returns (is_valid, error_message, problem_position_name)
    """
    from models import Position, Candidate
    
    # Group candidates by position
    position_totals = {}
    
    for candidate_id, vote_count in votes_data.items():
        candidate = Candidate.query.get(candidate_id)
        if not candidate:
            continue
        
        position_id = candidate.position_id
        if position_id not in position_totals:
            position_totals[position_id] = {
                'total': 0,
                'position_name': candidate.position_ref.title
            }
        position_totals[position_id]['total'] += int(vote_count or 0)
    
    # Check each position's total against stream's student count
    for position_id, data in position_totals.items():
        if data['total'] > stream.total_students:
            return False, data['position_name'], data['total']
    
    return True, None, None


def create_notification(stream, position_name, attempted_total):
    """Create a notification for admin when vote validation fails"""
    notification = Notification(
        stream_id=stream.id,
        message=f"Vote submission blocked: {stream.class_ref.name} - {stream.name}",
        attempted_total=attempted_total,
        max_allowed=stream.total_students,
        position_name=position_name
    )
    db.session.add(notification)
    db.session.commit()


def calculate_winners(election_id):
    """Calculate winners for all positions in an election"""
    positions = Position.query.filter_by(election_id=election_id).all()
    results = {}
    
    for position in positions:
        candidate_votes = []
        for candidate in position.candidates:
            total = db.session.query(db.func.sum(VoteTally.vote_count))\
                .join(VoteSubmission)\
                .join(Candidate)\
                .filter(VoteTally.candidate_id == candidate.id)\
                .scalar() or 0
            candidate_votes.append({
                'candidate_id': candidate.id,
                'candidate_name': candidate.name,
                'votes': total
            })
        
        # Sort by votes descending
        candidate_votes.sort(key=lambda x: x['votes'], reverse=True)
        
        # Assign ranks (handle ties)
        rank = 1
        prev_votes = None
        for i, cv in enumerate(candidate_votes):
            if prev_votes is not None and cv['votes'] < prev_votes:
                rank = i + 1
            cv['rank'] = rank
            prev_votes = cv['votes']
        
        results[position.title] = candidate_votes
    
    return results
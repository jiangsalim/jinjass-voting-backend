from flask import Blueprint, request, jsonify
from models import db, Notification
from utils.decorators import admin_required

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications', methods=['GET'])
@admin_required
def get_notifications(teacher):
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    
    unread_count = Notification.query.filter_by(is_read=False).count()

    return jsonify({
        'unread_count': unread_count,
        'notifications': [{
            'id': n.id,
            'message': n.message,
            'position_name': n.position_name,
            'attempted_total': n.attempted_total,
            'max_allowed': n.max_allowed,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        } for n in notifications]
    })

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@admin_required
def mark_as_read(teacher, notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'})

@notifications_bp.route('/api/notifications/read-all', methods=['PUT'])
@admin_required
def mark_all_as_read(teacher):
    Notification.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'})
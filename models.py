from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ==================== SYSTEM SETTINGS ====================
class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    voting_open = db.Column(db.Boolean, default=False)
    current_election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=True)
    display_type = db.Column(db.String(20), default='graphs')  # 'graphs' or 'counts'

# ==================== TEACHERS ====================
class Teacher(UserMixin, db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== ELECTIONS ====================
class Election(db.Model):
    __tablename__ = 'elections'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    classes = db.relationship('Class', backref='election_ref', lazy=True, cascade='all, delete-orphan')
    positions = db.relationship('Position', backref='election_ref', lazy=True, cascade='all, delete-orphan')

# ==================== CLASSES ====================
class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)

    streams = db.relationship('Stream', backref='class_ref', lazy=True, cascade='all, delete-orphan')

# ==================== STREAMS ====================
class Stream(db.Model):
    __tablename__ = 'streams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    total_students = db.Column(db.Integer, nullable=False)

    submission = db.relationship('VoteSubmission', backref='stream_ref', uselist=False, cascade='all, delete-orphan')

# ==================== POSITIONS ====================
class Position(db.Model):
    __tablename__ = 'positions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)

    candidates = db.relationship('Candidate', backref='position_ref', lazy=True, cascade='all, delete-orphan')

# ==================== CANDIDATES ====================
class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=False)

    tallies = db.relationship('VoteTally', backref='candidate_ref', lazy=True, cascade='all, delete-orphan')

# ==================== VOTE SUBMISSIONS ====================
class VoteSubmission(db.Model):
    __tablename__ = 'vote_submissions'
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('streams.id'), unique=True, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    tallies = db.relationship('VoteTally', backref='submission_ref', lazy=True, cascade='all, delete-orphan')
    teacher = db.relationship('Teacher', backref='submissions')  # ADD THIS LINE
# ==================== VOTE TALLIES ====================
class VoteTally(db.Model):
    __tablename__ = 'vote_tallies'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('vote_submissions.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    vote_count = db.Column(db.Integer, nullable=False, default=0)

# ==================== NOTIFICATIONS ====================
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('streams.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    attempted_total = db.Column(db.Integer, nullable=True)
    max_allowed = db.Column(db.Integer, nullable=True)
    position_name = db.Column(db.String(100), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
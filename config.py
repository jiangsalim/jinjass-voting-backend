import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jinjass-voting-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///voting.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
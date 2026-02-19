# progress tracking model

from backend.database.db import db
from datetime import datetime
import json

class UserProgress(db.Model):
    __tablename__ = "user_progress"

    progress_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_attempts = db.Column(db.Integer, default=0)
    words_mastered = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_practice_date = db.Column(db.Date)
    total_practice_time = db.Column(db.Integer, default=0)  # in seconds
    problematic_phonemes = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id):
        self.user_id = user_id

    def set_problematic_phonemes(self, phonemes_dict):
        """Store problematic phonemes as JSON"""
        self.problematic_phonemes = json.dumps(phonemes_dict)

    def get_problematic_phonemes(self):
        """Retrieve problematic phonemes as dict"""
        if self.problematic_phonemes:
            return json.loads(self.problematic_phonemes)
        return {}

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'user_id': self.user_id,
            'total_attempts': self.total_attempts,
            'words_mastered': self.words_mastered,
            'average_score': round(self.average_score, 2),
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_practice_date': self.last_practice_date.isoformat() if self.last_practice_date else None,
            'total_practice_time': self.total_practice_time,
            'problematic_phonemes': self.get_problematic_phonemes()
        }

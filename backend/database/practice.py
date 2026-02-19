# practice history model

from backend.database.db import db
from datetime import datetime
import json

class PracticeAttempt(db.Model):
    __tablename__ = "practice_attempts"

    attempt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_word = db.Column(db.String(500), nullable=False)
    target_type = db.Column(db.String(20), default='word')  # 'word' or 'sentence'
    audio_path = db.Column(db.String(500), nullable=False)
    transcript = db.Column(db.String(500))
    score = db.Column(db.Float, default=0.0)
    phoneme_errors = db.Column(db.Text)  # JSON string
    ai_feedback = db.Column(db.Text)
    ai_tips = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_mastered = db.Column(db.Boolean, default=False)
    attempt_number = db.Column(db.Integer, default=1)  # Track attempt count for same word

    def __init__(self, user_id, target_word, audio_path, target_type='word'):
        self.user_id = user_id
        self.target_word = target_word
        self.audio_path = audio_path
        self.target_type = target_type

    def set_phoneme_errors(self, errors_dict):
        """Store phoneme errors as JSON"""
        self.phoneme_errors = json.dumps(errors_dict)

    def get_phoneme_errors(self):
        """Retrieve phoneme errors as dict"""
        if self.phoneme_errors:
            return json.loads(self.phoneme_errors)
        return {}

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'attempt_id': self.attempt_id,
            'user_id': self.user_id,
            'target_word': self.target_word,
            'target_type': self.target_type,
            'audio_path': self.audio_path,
            'transcript': self.transcript,
            'score': self.score,
            'phoneme_errors': self.get_phoneme_errors(),
            'ai_feedback': self.ai_feedback or "Keep practicing!",
            'ai_tips': self.ai_tips or "Listen to the reference audio.",
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_mastered': self.is_mastered,
            'attempt_number': self.attempt_number
        }



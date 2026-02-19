# progress analytics

from backend.database.practice import PracticeAttempt
from backend.database.progress import UserProgress
from backend.database.db import db
from datetime import datetime, timedelta, date
from collections import Counter
from sqlalchemy import func
from loguru import logger

class ProgressService:
    
    @staticmethod
    def update_user_progress(user_id: int, new_attempt: PracticeAttempt):
        logger.info(f"Updating progress for User ID: {user_id} after attempt on '{new_attempt.target_word}'")
        progress = UserProgress.query.filter_by(user_id=user_id).first()
        
        if not progress:
            progress = UserProgress(user_id=user_id)
            progress.total_attempts = 0
            progress.words_mastered = 0
            progress.average_score = 0.0
            progress.current_streak = 0
            progress.longest_streak = 0
            db.session.add(progress)
        
        # Update total attempts
        progress.total_attempts = (progress.total_attempts or 0) + 1
        
        # Update words mastered count
        if new_attempt.is_mastered:
            logger.debug(f"Attempt mastered. Checking if '{new_attempt.target_word}' was previously mastered by User {user_id}")
            # Check if this word was already mastered
            prev_mastered = PracticeAttempt.query.filter_by(
                user_id=user_id,
                target_word=new_attempt.target_word,
                is_mastered=True
            ).filter(PracticeAttempt.attempt_id != new_attempt.attempt_id).first()
            
            if not prev_mastered:
                progress.words_mastered += 1
                logger.success(f"New word mastered! Total mastered for User {user_id}: {progress.words_mastered}")
        
        # Recalculate average score
        avg_score = db.session.query(func.avg(PracticeAttempt.score)).filter_by(
            user_id=user_id
        ).scalar()
        progress.average_score = float(avg_score) if avg_score else 0.0
        
        # Update streak
        today = date.today()
        if progress.last_practice_date:
            days_diff = (today - progress.last_practice_date).days
            if days_diff == 0:
                # Same day, streak continues
                pass
            elif days_diff == 1:
                # Consecutive day
                progress.current_streak += 1
                if progress.current_streak > progress.longest_streak:
                    progress.longest_streak = progress.current_streak
            else:
                # Streak broken
                progress.current_streak = 1
        else:
            # First practice
            progress.current_streak = 1
            progress.longest_streak = 1
        
        progress.last_practice_date = today
        
        # Update problematic phonemes
        ProgressService._update_problematic_phonemes(user_id, progress)
        
        db.session.commit()
    
    @staticmethod
    def _update_problematic_phonemes(user_id: int, progress: UserProgress):
        # Get recent attempts with errors
        logger.debug(f"Analyzing recent attempts for User {user_id} to update problematic phonemes")
        recent_attempts = PracticeAttempt.query.filter_by(
            user_id=user_id
        ).order_by(PracticeAttempt.timestamp.desc()).limit(20).all()
        
        phoneme_error_counts = Counter()
        
        for attempt in recent_attempts:
            errors = attempt.get_phoneme_errors()
            for phoneme in errors.keys():
                phoneme_error_counts[phoneme] += 1
        
        # Get top 5 problematic phonemes
        top_problematic = dict(phoneme_error_counts.most_common(5))
        progress.set_problematic_phonemes(top_problematic)
    
    @staticmethod
    def get_user_statistics(user_id: int):
        logger.debug(f"Fetching statistics for User ID: {user_id}")
        progress = UserProgress.query.filter_by(user_id=user_id).first()
        
        if not progress:
            logger.warning(f"No progress record found for User ID: {user_id}")
            return {
                'total_attempts': 0,
                'words_mastered': 0,
                'average_score': 0.0,
                'current_streak': 0,
                'longest_streak': 0,
                'total_practice_time': 0,
                'problematic_phonemes': {}
            }
        
        return progress.to_dict()
    
    @staticmethod
    def get_practice_history(user_id: int, limit: int = 50, word: str = None):
        query = PracticeAttempt.query.filter_by(user_id=user_id)
        
        if word:
            query = query.filter_by(target_word=word)
        
        attempts = query.order_by(
            PracticeAttempt.timestamp.desc()
        ).limit(limit).all()
        
        return [attempt.to_dict() for attempt in attempts]
    
    @staticmethod
    def get_word_attempts(user_id: int, target_word: str):
        attempts = PracticeAttempt.query.filter_by(
            user_id=user_id,
            target_word=target_word
        ).order_by(PracticeAttempt.timestamp.asc()).all()
        
        return [attempt.to_dict() for attempt in attempts]
    
    @staticmethod
    def get_mastered_words(user_id: int):
        mastered = db.session.query(PracticeAttempt.target_word).filter_by(
            user_id=user_id,
            is_mastered=True
        ).distinct().all()
        
        return [word[0] for word in mastered]
    
    @staticmethod
    def get_improvement_trend(user_id: int, days: int = 7):

        since_date = datetime.utcnow() - timedelta(days=days)
        
        attempts = PracticeAttempt.query.filter(
            PracticeAttempt.user_id == user_id,
            PracticeAttempt.timestamp >= since_date
        ).order_by(PracticeAttempt.timestamp.asc()).all()
        
        if not attempts:
            return {
                'trend': 'neutral',
                'score_change': 0,
                'attempts_count': 0
            }
        
        # Calculate average of first half vs second half
        mid_point = len(attempts) // 2
        first_half_avg = sum(a.score for a in attempts[:mid_point]) / max(mid_point, 1)
        second_half_avg = sum(a.score for a in attempts[mid_point:]) / max(len(attempts) - mid_point, 1)
        
        score_change = second_half_avg - first_half_avg
        
        if score_change > 5:
            trend = 'improving'
        elif score_change < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'score_change': round(score_change, 2),
            'attempts_count': len(attempts),
            'period_days': days
        }
    
    @staticmethod
    def get_next_attempt_number(user_id: int, target_word: str):
        max_attempt = db.session.query(
            func.max(PracticeAttempt.attempt_number)
        ).filter_by(
            user_id=user_id,
            target_word=target_word
        ).scalar()
        next_val = (max_attempt or 0) + 1
        logger.debug(f"Next attempt number for User {user_id} on '{target_word}': {next_val}")
        return (max_attempt or 0) + 1

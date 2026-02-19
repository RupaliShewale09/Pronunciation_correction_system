# ai tutor endpoint

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from backend.database.db import db
from backend.database.practice import PracticeAttempt
from backend.services.gemini_service import get_gemini_service
from backend.services.progress_service import ProgressService
from backend.services.pronunciation_service import process_audio
from backend.services.tts_service import get_tts_stream
from backend.utils.audio_utils import convert_audio_to_wav

from loguru import logger

ai_tutor_bp = Blueprint("ai_tutor", __name__)
PRACTICE_UPLOAD_FOLDER = "practice_uploads"

if not os.path.exists(PRACTICE_UPLOAD_FOLDER):
    os.makedirs(PRACTICE_UPLOAD_FOLDER)


@ai_tutor_bp.route("/generate-words", methods=["POST"])
@jwt_required()
def generate_practice_words():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        difficulty = data.get("difficulty", "medium")
        
        # Get user's problematic phonemes
        stats = ProgressService.get_user_statistics(current_user_id) or {}
        problematic_phonemes = list(stats.get('problematic_phonemes', {}).keys())
        
        # Get mastered words
        mastered_words = ProgressService.get_mastered_words(current_user_id) or []
        
        # Get Gemini service
        gemini = get_gemini_service()
        if not gemini:
            logger.warning("Gemini service unavailable — returning fallback suggestions")
            return jsonify({
                "error": "AI service unavailable",
                "suggestions": [
                    {"word": "practice", "reason": "Common word for pronunciation practice"},
                    {"word": "think", "reason": "Practice the 'th' sound"},
                    {"word": "world", "reason": "Practice 'r' and 'l' sounds"}
                ]
            }), 200
        logger.debug("Calling Gemini for suggestions...")
        # Generate suggestions
        suggestions = gemini.suggest_practice_words(
            problematic_phonemes=problematic_phonemes,
            mastered_words=mastered_words,
            difficulty_level=difficulty
        )
        
        if not suggestions or not isinstance(suggestions, list):
            logger.error("Gemini returned invalid suggestions format")
            raise ValueError("Invalid AI response")


        return jsonify({
            "suggestions": suggestions[:5],
            "based_on_phonemes": problematic_phonemes,
            "mastered_count": len(mastered_words),
            "ai_available": True
        })

    except Exception as e:
        logger.exception("Error in generate_practice_words")
        return jsonify({
            "error": "Failed to generate suggestions",
            "details": str(e)
        }), 500


@ai_tutor_bp.route("/practice", methods=["POST"])
@jwt_required()
def submit_practice_attempt():
    current_user_id = get_jwt_identity()
    logger.info(f"New practice attempt started - User ID: {current_user_id}")

    try:
        
        if "audio" not in request.files:
            logger.warning(f"User {current_user_id} submitted without audio file.")
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files["audio"]
        target_word = request.form.get("target_word", "").strip()
        target_type = request.form.get("target_type", "word")
        mode = request.form.get("mode", "ml")
        
        if not target_word:
            logger.warning(f"User {current_user_id} missing target_word.")
            return jsonify({"error": "Target word/sentence is required"}), 400
        logger.info(f"Processing word: '{target_word}' | Mode: {mode} for User: {current_user_id}")
        # Save and process audio
        raw_path = os.path.join(PRACTICE_UPLOAD_FOLDER, f"raw_{current_user_id}_{target_word[:20]}.tmp")
        file.save(raw_path)
        
        # Convert to proper format
        processed_filename = f"practice_{current_user_id}_{target_word[:20]}.wav"
        processed_path = os.path.join(PRACTICE_UPLOAD_FOLDER, processed_filename)
        
        try:
            convert_audio_to_wav(raw_path, processed_path)
            logger.debug(f"Audio converted successfully for User {current_user_id}: {processed_path}")
        except Exception as e:
            return jsonify({"error": f"Audio conversion failed: {str(e)}"}), 500
        finally:
            if os.path.exists(raw_path):
                os.remove(raw_path)
        
        # Analyze pronunciation
        logger.info(f"Starting ML analysis for '{target_word}'")
        analysis = process_audio(processed_path, mode)
        logger.info(f"analysis done - {analysis}")
        if analysis.get("error"):
            logger.error(f"ML Processing error: {analysis['error']}")
            return jsonify({
                "error": analysis["error"],
                "transcript": analysis.get("transcript", "")
            }), 500
        
        # Calculate granular score
        results = analysis.get("results", [])

        if not results:
            score = 30.0  # Minimum floor if no speech detected
        else:
            # Example: [0.75, 0.5, 0.85] -> sum is 2.1
            total_confidence = sum(float(r.get("confidence", 0) or 0) for r in results)
            
            # Example: 2.1 / 3 = 0.7
            avg_confidence = total_confidence / len(results)
            
            # Formula: 30 + (0.7 * 70) = 30 + 49 = 79.0%
            score = 30 + (avg_confidence * 70)

        # Final score ko rounding de dein
        score = round(min(100.0, score), 2)
        
        # Get phoneme errors
        phoneme_errors = {}
        for word_result in analysis.get("results", []):
            if word_result.get("status") == "wrong":
                word = word_result.get("word")
                phoneme_errors[word] = {
                    "correction": word_result.get("correction"),
                    "heard": analysis.get("transcript", "")
                }
        
        # Determine if mastered
        is_mastered = score >= 80
        
        # Get attempt number for this word
        attempt_number = ProgressService.get_next_attempt_number(current_user_id, target_word)
        
        # Create practice attempt record
        attempt = PracticeAttempt(
            user_id=current_user_id,
            target_word=target_word,
            audio_path=processed_path,
            target_type=target_type
        )
        attempt.transcript = analysis.get("transcript", "")
        attempt.score = score
        attempt.set_phoneme_errors(phoneme_errors)
        attempt.is_mastered = is_mastered
        attempt.attempt_number = attempt_number
        
        # Get AI feedback
        gemini = get_gemini_service()
        if gemini:
            try:
                ai_response = gemini.generate_feedback(
                    target_word=target_word,
                    transcript=attempt.transcript,
                    phoneme_errors=phoneme_errors,
                    score=score
                )
                attempt.ai_feedback = ai_response.get("feedback")
                attempt.ai_tips = ai_response.get("tips")
            except Exception as e:
                logger.error(f"Gemini feedback failed: {e}")
                attempt.ai_feedback = "Good effort! Keep practicing."
                attempt.ai_tips = "Focus on clear pronunciation of each sound."
        else:
            attempt.ai_feedback = f"Score: {score:.1f}%. Keep practicing!"
            attempt.ai_tips = "Listen carefully to the reference pronunciation."
        
        # Save to database
        db.session.add(attempt)
        db.session.commit()
        
        # Update user progress
        ProgressService.update_user_progress(current_user_id, attempt)
        logger.success(f"Practice saved: User {current_user_id}, Word: '{target_word}', Score: {score}%")

        # Return response
        return jsonify({
            "attempt_id": attempt.attempt_id,
            "target_word": target_word,
            "transcript": attempt.transcript,
            "score": round(score, 2),
            "is_mastered": is_mastered,
            "attempt_number": attempt_number,
            "ai_feedback": attempt.ai_feedback,
            "ai_tips": attempt.ai_tips,
            "phoneme_errors": phoneme_errors,
            "results": analysis.get("results", [])
        })
    
    except Exception as e:
        logger.critical(f"Unhandled exception in /practice: {str(e)}")
        return jsonify({"error": str(e)}), 500


@ai_tutor_bp.route("/history", methods=["GET"])
@jwt_required()
def get_practice_history():
    try:
        current_user_id = get_jwt_identity()
        limit = int(request.args.get("limit", 50))
        word = request.args.get("word")
        
        history = ProgressService.get_practice_history(
            user_id=current_user_id,
            limit=limit,
            word=word
        )
        
        return jsonify({
            "history": history,
            "count": len(history)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_tutor_bp.route("/word-history/<word>", methods=["GET"])
@jwt_required()
def get_word_specific_history(word):
    """
    Get all attempts for a specific word
    """
    try:
        current_user_id = get_jwt_identity()
        
        attempts = ProgressService.get_word_attempts(
            user_id=current_user_id,
            target_word=word
        )
        
        return jsonify({
            "word": word,
            "attempts": attempts,
            "total_attempts": len(attempts)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_tutor_bp.route("/progress", methods=["GET"])
@jwt_required()
def get_progress_report():
    """
    Get comprehensive progress report with AI insights
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get statistics
        stats = ProgressService.get_user_statistics(current_user_id)
        
        # Get recent attempts for AI analysis
        recent_attempts = ProgressService.get_practice_history(
            user_id=current_user_id,
            limit=10
        )
        
        # Get improvement trend
        trend = ProgressService.get_improvement_trend(current_user_id, days=7)
        
        # Generate AI report
        gemini = get_gemini_service()
        ai_report = None
        if not gemini:
            logger.warning(f"!!! FALLBACK TRIGGERED !!! Gemini Service NULL for Progress Report. User {current_user_id}")
        elif stats.get('total_attempts', 0) == 0:
             logger.info(f"No attempts for user {current_user_id}, skipping AI report.")

        if gemini and stats.get('total_attempts', 0) > 0:
            try:
                ai_report = gemini.generate_progress_report(
                    user_stats=stats,
                    recent_attempts=recent_attempts
                )
            except Exception as e:
                print(f"Gemini report error: {e}")
        
        return jsonify({
            "statistics": stats,
            "recent_attempts": recent_attempts,
            "improvement_trend": trend,
            "ai_report": ai_report
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_tutor_bp.route("/mastered-words", methods=["GET"])
@jwt_required()
def get_mastered_words():
    """
    Get list of words user has mastered
    """
    try:
        current_user_id = get_jwt_identity()
        mastered = ProgressService.get_mastered_words(current_user_id)
        
        return jsonify({
            "mastered_words": mastered,
            "count": len(mastered)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_tutor_bp.route("/listen-word", methods=["GET"])
def listen_word():
    """
    Get TTS audio for a word (reference pronunciation)
    
    Query params:
    - text: word/sentence to speak
    """
    text = request.args.get('text')
    if not text:
        return "Text is required", 400
    
    audio_stream = get_tts_stream(text)
    
    return send_file(
        audio_stream,
        mimetype="audio/mpeg",
        as_attachment=False
    )

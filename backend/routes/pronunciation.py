# pronunciation analysis
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from backend.services.pronunciation_service import process_audio
from backend.services.tts_service import get_tts_stream
from backend.utils.audio_utils import convert_audio_to_wav

pronun_bp = Blueprint("pronunciation", __name__)
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@pronun_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze():
    try:
        current_user_id = get_jwt_identity()

        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        file = request.files["audio"]
        mode = request.form.get("mode", "ml")

        # 1. Save the raw file from the browser (usually .webm or .blob)
        raw_path = os.path.join(UPLOAD_FOLDER, f"raw_{file.filename}.tmp")
        file.save(raw_path)

        # 2. Convert to 16kHz, Mono, WAV (Required for your ASR engines)
        processed_filename = f"processed_{current_user_id}.wav"
        processed_path = os.path.join(UPLOAD_FOLDER, processed_filename)
        
        try:
            convert_audio_to_wav(raw_path, processed_path)
        except Exception as e:
            return jsonify({"error": f"Audio conversion failed: {str(e)}"}), 500
        finally:
            # Clean up the raw file to save space
            if os.path.exists(raw_path):
                os.remove(raw_path)
    

        # 3. Process the compatible audio file
        result = process_audio(processed_path, mode)

        # 4. Return results structured for your dashboard.html
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "transcript": "Error during analysis"}), 500
    



@pronun_bp.route('/listen', methods=['GET'])
def listen():

    text = request.args.get('text')
    if not text:
        return "Text is required", 400

    audio_stream = get_tts_stream(text)

    return send_file(
        audio_stream,
        mimetype="audio/mpeg",
        as_attachment=False  
    )
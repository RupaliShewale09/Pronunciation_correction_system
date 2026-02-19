from backend.speech_engine.core.asr import transcribe_audio as rule_transcribe
from backend.speech_engine.core.evaluator import evaluate_word as rule_evaluate
from backend.speech_engine.ml_core.asr import transcribe_audio as ml_transcribe
from backend.speech_engine.ml_core.evaluator import evaluate_word as ml_evaluate

from backend.services.gemini_service import get_gemini_service
from loguru import logger

def process_audio(audio_path, mode="ml"):

    if mode == "ml":
        transcript, words = ml_transcribe(audio_path)
        evaluator = ml_evaluate
    elif mode == "rule":
        transcript, words = rule_transcribe(audio_path)
        evaluator = rule_evaluate
    else:
        return {
            "transcript": "",
            "error": f"Invalid mode selected: {mode}",
            "results": []
        }

    if transcript.startswith("Error") or transcript.startswith("ASR Error"):
        return {
            "transcript": "",
            "error": transcript,
            "results": []
        }

    results = [evaluator(word) for word in words]
    wrong_words = [r for r in results if r.get("status") == "wrong"]

    grammar_result = None
    try: 
        if len(words) > 1:
            gemini = get_gemini_service()
            if gemini:
                grammar_result = gemini.check_grammar(transcript)
    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        grammar_result = {"status": "error"}
    
    return {
        "transcript": transcript,
        "results": results,
        "wrong_words": wrong_words,
        "grammar" : grammar_result
    }

import wave
import json
import os
from vosk import Model, KaldiRecognizer

# Path to your extracted Vosk model
MODEL_PATH = "backend/speech_engine/vosk_model/vosk-model-small-en-us-0.15"

# Load model once at the start
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model folder not found at: {MODEL_PATH}")

model = Model(MODEL_PATH)

def transcribe_audio(audio_path):
    """
    Transcribes audio exactly as spoken without auto-correction.
    Returns: (transcript_string, list_of_words)
    """
    try:
        wf = wave.open(audio_path, "rb")
        
       # Strict Vosk requirements
        if wf.getnchannels() != 1:
            wf.close()
            return "Error: Audio must be MONO", []

        if wf.getsampwidth() != 2:
            wf.close()
            return "Error: Audio must be 16-bit PCM", []

        if wf.getframerate() != 16000:
            wf.close()
            return "Error: Audio must be 16kHz sample rate", []
        
        # Recognizer setup
        rec = KaldiRecognizer(model, 16000)
        rec.SetWords(True) # This helps in getting exact word-by-word sounds

        transcript_parts = []
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break

            if rec.AcceptWaveform(data):
                # Result contains the raw recognized text
                result = json.loads(rec.Result())
                if result.get("text"):
                    transcript_parts.append(result["text"])

        # Final result from the remaining audio buffer
        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            transcript_parts.append(final_result["text"])

        wf.close()

        transcript = " ".join(transcript_parts).strip()
        words = [w for w in transcript.split() if w]

        return transcript, words

    except Exception as e:
        return f"ASR Error: {str(e)}", []
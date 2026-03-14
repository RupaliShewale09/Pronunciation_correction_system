import pandas as pd
from difflib import SequenceMatcher
import cmudict
import re

# Load CMU for fallback
try:
    cmu = cmudict.dict()
except Exception:
    cmu = None

try:
    df = pd.read_csv("backend/speech_engine/ml_core/daily_use_pronunciation_dataset.csv")
except Exception:
    df = None

def clean_word(word):
    """Removes punctuation and converts to lowercase."""
    return re.sub(r"[^\w]", "", word.lower())

def evaluate_word(word, predicted_phoneme_list):
    """
    ML-based evaluation comparing Whisper output against Ground Truth.
    """
    clean = clean_word(word)
    
    if df is None:
        return {"word": word, "status": "error", "message": "Dataset not found"}

    target_phonemes = []
    source = ""

    # --- STEP 1: Try CSV Dataset ---
    match = df[df['word'] == clean]
    if not match.empty:
        raw_phonemes = match.iloc[0]['correct_phonemes'].split()
        target_phonemes = [re.sub(r"\d", "", p) for p in raw_phonemes]
        source = "dataset"
    
    # --- STEP 2: Fallback to CMU Dictionary ---
    elif cmu and clean in cmu:
        # Use first pronunciation variant
        raw_phonemes = cmu[clean][0]
        target_phonemes = [re.sub(r"\d", "", p) for p in raw_phonemes]
        source = "cmu_dict"
    
    # --- STEP 3: If word not found anywhere ---
    else:
        return {
            "word": word,
            "status": "unknown",
            "message": "Word not in training set or dictionary"
        }

    # --- STEP 4: Strict Comparison ---
    if not predicted_phoneme_list:
        return {"word": word, "status": "wrong", "score": 0}

    # Clean predicted phonemes of any numbers just in case
    clean_predicted = [re.sub(r"\d", "", p).upper() for p in predicted_phoneme_list]
    
    # Convert to strings for exact sequence matching
    target_str = "".join(target_phonemes).upper()
    predicted_str = "".join(clean_predicted).upper()
    
    # Use SequenceMatcher for a similarity score
    score = SequenceMatcher(None, target_str, predicted_str).ratio()

    # Rule-based threshold for 'Correct' (85% similarity)
    if score >= 0.85: 
        return {
            "word": word,
            "status": "correct",
            "score": round(score, 2),
            "source": source
        }
    
    # If it's wrong, return details for the frontend
    return {
        "word": word,
        "status": "wrong",
        "correction": " ".join(target_phonemes),
        "actual_heard": " ".join(clean_predicted),
        "score": round(score, 2),
        "source": source
    }
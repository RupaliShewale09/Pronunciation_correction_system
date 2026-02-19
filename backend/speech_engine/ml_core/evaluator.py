import cmudict
from difflib import SequenceMatcher
import re

cmu = cmudict.dict()

def clean_word(word):
    return re.sub(r"[^\w]", "", word.lower())

def phonemes_to_readable(phonemes):
    mapping = {
        "AA": "ah", "AE": "a", "AH": "uh", "AO": "aw",
        "AW": "ow", "AY": "eye", "EH": "eh", "ER": "ur",
        "EY": "ay", "IH": "ih", "IY": "ee", "OW": "oh",
        "OY": "oy", "UH": "uh", "UW": "oo"
    }
    
    readable = []
    for p in phonemes:
        p_clean = re.sub(r"\d", "", p)  # Stress numbers hatao
        readable.append(mapping.get(p_clean, p_clean.lower()))
    
    return "-".join(readable)

def phoneme_similarity(phonemes, spoken_word):
    expected = "".join([re.sub(r"\d", "", p) for p in phonemes])
    spoken = spoken_word.upper()
    return SequenceMatcher(None, expected, spoken).ratio()

def evaluate_word(word):
    clean = clean_word(word)

    if not clean or clean not in cmu:
        return {
            "word": word,
            "status": "unknown"
        }

    phonemes = cmu[clean][0]
    score = phoneme_similarity(phonemes, clean)

    # ML Score check
    if score >= 0.90:
        return {
            "word": word,
            "status": "correct"
        }

    return {
        "word": word,
        "status": "wrong",
        "correction": phonemes_to_readable(phonemes), 
        "confidence": score
    }
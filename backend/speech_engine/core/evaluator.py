import re
import cmudict

CMU_DICT = cmudict.dict()

# Words with long / complex phonemes usually mispronounced
PHONEME_COMPLEXITY_THRESHOLD = 5


def clean_word(word):
    return re.sub(r"[^\w]", "", word.lower())


def phonemes_to_readable(phonemes):
    """
    Convert CMU phonemes to human-readable pronunciation
    """
    mapping = {
        "AA": "ah", "AE": "a", "AH": "uh", "AO": "aw",
        "AW": "ow", "AY": "eye", "EH": "eh", "ER": "ur",
        "EY": "ay", "IH": "ih", "IY": "ee", "OW": "oh",
        "OY": "oy", "UH": "uh", "UW": "oo"
    }

    readable = []
    for p in phonemes:
        p = re.sub(r"\d", "", p)  # remove stress numbers
        readable.append(mapping.get(p, p.lower()))

    return "-".join(readable)


def evaluate_word(word):
    clean = clean_word(word)

    if not clean or clean not in CMU_DICT:
        return {"word": word, "status": "unknown"}

    phonemes = CMU_DICT[clean][0]

    # Decide if pronunciation needs guidance
    if len(phonemes) >= PHONEME_COMPLEXITY_THRESHOLD:
        return {
            "word": word,
            "status": "wrong",
            "correction": phonemes_to_readable(phonemes)
        }

    return {"word": word, "status": "correct"}

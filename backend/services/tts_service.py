from gtts import gTTS
from io import BytesIO

def get_tts_stream(text):
    """Generates an in-memory MP3 file for a given string."""
    mp3_fp = BytesIO()
    tts = gTTS(text=text, lang='en')
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp
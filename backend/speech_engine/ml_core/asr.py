import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

TEXT_MODEL_ID = "openai/whisper-base"
PHONEME_MODEL_PATH = "backend/speech_engine/ml_core/final_model"

device = "cuda" if torch.cuda.is_available() else "cpu"

text_processor = None
text_model = None
phoneme_processor = None
phoneme_model = None


def load_models():
    global text_processor, text_model, phoneme_processor, phoneme_model

    if text_model is None:
        text_processor = WhisperProcessor.from_pretrained(TEXT_MODEL_ID)
        text_model = WhisperForConditionalGeneration.from_pretrained(TEXT_MODEL_ID).to(device)
        text_model.eval()

    if phoneme_model is None:
        phoneme_processor = WhisperProcessor.from_pretrained(PHONEME_MODEL_PATH)
        phoneme_model = WhisperForConditionalGeneration.from_pretrained(PHONEME_MODEL_PATH).to(device)
        phoneme_model.eval()

def transcribe_audio(audio_path):
    """
    Input: Path to user audio (.wav, 16kHz recommended)
    Output: List of predicted phonemes (based purely on sound)
    """
    load_models()

    # 1️⃣ WORD TRANSCRIPTION
    speech, _ = librosa.load(audio_path, sr=16000)

    text_inputs = text_processor(
        speech,
        sampling_rate=16000,
        return_tensors="pt"
    ).input_features.to(device)

    with torch.no_grad():
        text_ids = text_model.generate(
            text_inputs,
            language="en", 
            task="transcribe"
        )

    transcript = text_processor.batch_decode(
        text_ids,
        skip_special_tokens=True
    )[0].lower()

    words = [w for w in transcript.split() if w]

    # 2️⃣ PHONEME PREDICTION
    phoneme_inputs = phoneme_processor(
        speech,
        sampling_rate=16000,
        return_tensors="pt"
    ).input_features.to(device)

    with torch.no_grad():
        phoneme_ids = phoneme_model.generate(
            phoneme_inputs,
            language="en",
            task="transcribe"
        )

    phoneme_output = phoneme_processor.batch_decode(
        phoneme_ids,
        skip_special_tokens=True
    )[0]

    phoneme_list = phoneme_output.strip().split()

    return transcript, words, phoneme_list

if __name__ == "__main__":
    TEST_AUDIO = "uploads/processed_1.wav" 
    
    try:
        print(f"--- Testing ML Core on: {TEST_AUDIO} ---")
        
        # Run transcription
        transcript, words, phonemes = transcribe_audio(TEST_AUDIO)
        
        print(f"\n[1] Predicted Transcript: {transcript}")
        print(f"[2] Tokenized Words: {words}")
        print(f"[3] Predicted Phonemes: {phonemes}")
        
        # Basic sanity check
        if len(phonemes) > 0:
            print("\n✅ Success: Phoneme model is generating output.")
        else:
            print("\n❌ Warning: Phoneme model output is empty.")
            
    except Exception as e:
        print(f"An error occurred during testing: {e}")
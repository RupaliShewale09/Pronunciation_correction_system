import torch
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration


model_id = "openai/whisper-base" 

processor = WhisperProcessor.from_pretrained(model_id)
model = WhisperForConditionalGeneration.from_pretrained(model_id)

# Hardware check
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

def transcribe_audio(audio_path):
    """
    ML-based speech to text using Whisper-Base (Transformer).
    Optimized for laptop performance with zero auto-correction.
    """
    try:
        # 1. Load audio and resample to 16kHz
        speech, sr = librosa.load(audio_path, sr=16000)

        # 2. Pre-process
        input_features = processor(
            speech, 
            sampling_rate=16000, 
            return_tensors="pt"
        ).input_features.to(device)

        with torch.no_grad():
            # Strict mode: No creativity, No auto-correct
            predicted_ids = model.generate(
                input_features,
                do_sample=False, 
                temperature=0.0,
                language="en",
                task="transcribe",
                use_cache=True # Speed up inference on laptops
            )

        # 3. Decode output
        transcript = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

        words = [w for w in transcript.lower().split() if w]

        return transcript.lower(), words
    
    except Exception as e:
        return f"ASR Error: {str(e)}", []
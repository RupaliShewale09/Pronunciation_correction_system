import os
from pydub import AudioSegment
from loguru import logger


def convert_audio_to_wav(
    input_path: str,
    output_path: str,
    sample_rate: int = 16000,
    channels: int = 1,
    sample_width: int = 2
) -> str:
    """
    Convert any audio file to standardized WAV format.
    """
    try:
        audio = AudioSegment.from_file(input_path)
        audio = (
            audio
            .set_frame_rate(sample_rate)
            .set_channels(channels)
            .set_sample_width(sample_width)
        )
        audio.export(output_path, format="wav")
        logger.debug(f"Audio converted successfully → {output_path}")
        return output_path

    except Exception as e:
        logger.exception("Audio conversion failed")
        raise e

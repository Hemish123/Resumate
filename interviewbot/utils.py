from vosk import Model, KaldiRecognizer
import wave
import json
import subprocess
import tempfile
import os

# Use absolute path to your Vosk model folder
# Make sure this folder exists and contains model files
model_path = "C:/Users/Admin/Downloads/vosk-model-small-en-us-0.15"
vosk_model = Model(model_path)

def transcribe_audio_file(webm_file_path):
    """
    Converts webm audio to wav and transcribes using Vosk.
    """

    # Create a temp WAV filename, do NOT open yet
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        # Convert WebM -> WAV
        subprocess.run([
            "ffmpeg",
            "-y",  # overwrite
            "-i", webm_file_path,
            "-ar", "16000",
            "-ac", "1",
            wav_path
        ], check=True)

        # Open WAV safely
        with wave.open(wav_path, "rb") as wf:
            rec = KaldiRecognizer(vosk_model, wf.getframerate())
            results = []

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    results.append(result.get("text", ""))

            final_result = json.loads(rec.FinalResult())
            results.append(final_result.get("text", ""))

        transcript = " ".join(results).strip()
        return transcript

    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

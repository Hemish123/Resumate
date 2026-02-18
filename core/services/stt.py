
# import azure.cognitiveservices.speech as speechsdk

# from dotenv import load_dotenv
# load_dotenv()



# # -------------------------------------------------
# # ENV CONFIG
# # -------------------------------------------------

# AZURE_SPEECH_KEY = "4V9D92i5ho1m4QppDL228sTKG2dIT1JQhrHPzn0h8NaVCXAtoHqbJQQJ99BLACHYHv6XJ3w3AAAAACOGmD7P"
# AZURE_SPEECH_REGION = "eastus2"


# if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
#     raise RuntimeError("AZURE_SPEECH_KEY / AZURE_SPEECH_REGION not set")


# # -------------------------------------------------
# # MICROPHONE LISTEN
# # -------------------------------------------------

# def listen() -> str:
#     """
#     Uses Azure Speech-to-Text.
#     Listens from microphone and returns recognized text.
#     """

#     speech_config = speechsdk.SpeechConfig(
#         subscription=AZURE_SPEECH_KEY,
#         region=AZURE_SPEECH_REGION,
#     )

#     speech_config.speech_recognition_language = "en-US"

#     recognizer = speechsdk.SpeechRecognizer(
#         speech_config=speech_config
#     )

#     print("🎧 Listening...")

#     result = recognizer.recognize_once()

#     if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         return result.text.strip()

#     if result.reason == speechsdk.ResultReason.NoMatch:
#         print("⏳ No speech recognized")
#         return ""

#     if result.reason == speechsdk.ResultReason.Canceled:
#         details = speechsdk.CancellationDetails.from_result(result)
#         print("❌ Speech recognition canceled:", details.reason)
#         return ""

#     return ""































# core/services/stt.py

from pathlib import Path
import os
import azure.cognitiveservices.speech as speechsdk

from dotenv import load_dotenv


# -------------------------------------------------
# FORCE LOAD .env FROM PROJECT ROOT
# -------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


# -------------------------------------------------
# ENV CONFIG (READ FROM .env)
# -------------------------------------------------

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise RuntimeError(
        "AZURE_SPEECH_KEY / AZURE_SPEECH_REGION not set in .env"
    )


# -------------------------------------------------
# MICROPHONE LISTEN
# -------------------------------------------------

def listen() -> str:
    """
    Uses Azure Speech-to-Text.
    Listens from microphone and returns recognized text.
    """

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )

    speech_config.speech_recognition_language = "en-US"

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config
    )

    print("🎧 Listening...")

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text.strip()

    if result.reason == speechsdk.ResultReason.NoMatch:
        print("⏳ No speech recognized")
        return ""

    if result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.CancellationDetails.from_result(result)
        print("❌ Speech recognition canceled:", details.reason)
        return ""

    return ""


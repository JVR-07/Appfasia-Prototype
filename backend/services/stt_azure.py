import asyncio
import base64
from dataclasses import dataclass


@dataclass
class STTResult:
    transcript: str
    confidence: float
    is_low_confidence: bool

    @property
    def is_timeout(self) -> bool:
        return not self.transcript


class AzureSTTService:
    """
    Async wrapper around Azure Cognitive Speech SDK.
    When AZURE_SPEECH_KEY == 'mock', returns the provided expected_text
    directly (for dev/testing without Azure credits).
    """

    LOW_CONFIDENCE_THRESHOLD = 0.70

    def __init__(self, key: str, region: str) -> None:
        self._key = key
        self._region = region
        self._is_mock = key == "mock"

    async def transcribe_base64(
        self,
        audio_b64: str,
        expected_text: str | None = None,
        language: str = "es-MX",
    ) -> STTResult:
        if self._is_mock:
            return self._mock_result(expected_text)
        return await asyncio.get_event_loop().run_in_executor(
            None, self._transcribe_sync, audio_b64, language
        )

    def _mock_result(self, expected_text: str | None) -> STTResult:
        text = expected_text or ""
        return STTResult(
            transcript=text,
            confidence=0.95 if text else 0.0,
            is_low_confidence=not bool(text),
        )

    def _transcribe_sync(self, audio_b64: str, language: str) -> STTResult:
        import azure.cognitiveservices.speech as speechsdk  # noqa: PLC0415

        audio_bytes = base64.b64decode(audio_b64)

        speech_config = speechsdk.SpeechConfig(
            subscription=self._key, region=self._region
        )
        speech_config.speech_recognition_language = language

        stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=stream)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # Push bytes and close
        stream.write(audio_bytes)
        stream.close()

        result = recognizer.recognize_once()

        if result.reason.name == "RecognizedSpeech":
            confidence = result.json.get("Confidence", 0.5) if hasattr(result, "json") else 0.5
            is_low = confidence < self.LOW_CONFIDENCE_THRESHOLD
            return STTResult(
                transcript=result.text,
                confidence=confidence,
                is_low_confidence=is_low,
            )
        elif result.reason.name == "NoMatch":
            return STTResult(transcript="", confidence=0.0, is_low_confidence=True)
        else:
            return STTResult(transcript="", confidence=0.0, is_low_confidence=True)

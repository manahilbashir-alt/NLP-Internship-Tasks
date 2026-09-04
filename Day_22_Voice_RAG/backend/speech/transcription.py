from faster_whisper import WhisperModel


class TranscriptionService:
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        print(f"Loading Whisper model: {model_size}")

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )

        print("Whisper model loaded successfully.")

    def transcribe(self, audio_path: str):
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability,
        }


transcription_service = TranscriptionService()
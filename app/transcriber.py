from typing import Iterator


class TranscriptionResult:
    def __init__(self, text: str, start: float, end: float):
        self.text = text
        self.start = start
        self.end = end


class TranscriptionEngine:
    def __init__(self, model):
        self._model = model

    def transcribe(self, file_path: str) -> tuple[Iterator[TranscriptionResult], float]:
        segments, info = self._model.transcribe(
            file_path,
            language="ja",
            vad_filter=True,
        )

        def result_iter():
            for segment in segments:
                yield TranscriptionResult(
                    text=segment.text,
                    start=segment.start,
                    end=segment.end,
                )

        return result_iter(), info.duration

from app.transcriber import TranscriptionEngine


class FakeSegment:
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


class FakeInfo:
    def __init__(self, duration):
        self.duration = duration


class FakeModel:
    def __init__(self, segments, duration):
        self._segments = segments
        self._duration = duration
        self.last_call_kwargs = None

    def transcribe(self, file_path, **kwargs):
        self.last_call_kwargs = {"file_path": file_path, **kwargs}
        return iter(self._segments), FakeInfo(self._duration)


def test_transcribe_yields_text_and_duration():
    fake_segments = [
        FakeSegment("こんにちは。", 0.0, 2.0),
        FakeSegment("今日は会議です。", 2.0, 5.0),
    ]
    model = FakeModel(fake_segments, duration=5.0)
    engine = TranscriptionEngine(model)

    results, duration = engine.transcribe("/tmp/meeting.mp4")
    texts = [r.text for r in results]

    assert texts == ["こんにちは。", "今日は会議です。"]
    assert duration == 5.0


def test_transcribe_calls_model_with_japanese_and_vad():
    model = FakeModel([], duration=0.0)
    engine = TranscriptionEngine(model)

    list(engine.transcribe("/tmp/meeting.mp4")[0])

    assert model.last_call_kwargs["file_path"] == "/tmp/meeting.mp4"
    assert model.last_call_kwargs["language"] == "ja"
    assert model.last_call_kwargs["vad_filter"] is True

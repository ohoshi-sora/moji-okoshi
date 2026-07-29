from app.worker import TranscribeWorker


class FakeSegment:
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


class FakeEngine:
    def __init__(self, model):
        self.model = model

    def transcribe(self, file_path):
        segments = [
            FakeSegment("こんにちは", 0.0, 1.0),
            FakeSegment("さようなら", 1.0, 2.0),
        ]
        return iter(segments), 2.0


def fake_model_loader(model_size):
    return object()


def test_worker_emits_segments_and_final_text(qtbot):
    worker = TranscribeWorker(
        "/tmp/meeting.mp4",
        "medium",
        model_loader=fake_model_loader,
        engine_cls=FakeEngine,
    )

    segments = []
    worker.segment_ready.connect(segments.append)
    finished = []
    worker.finished_ok.connect(finished.append)

    worker.run()

    assert segments == ["こんにちは", "さようなら"]
    assert finished == ["こんにちはさようなら"]


def test_worker_emits_error_on_exception(qtbot):
    def broken_loader(model_size):
        raise RuntimeError("model load failed")

    worker = TranscribeWorker(
        "/tmp/meeting.mp4", "medium", model_loader=broken_loader, engine_cls=FakeEngine
    )

    errors = []
    worker.error.connect(errors.append)

    worker.run()

    assert errors == ["model load failed"]


def test_worker_cancel_stops_before_finished(qtbot):
    worker = TranscribeWorker(
        "/tmp/meeting.mp4", "medium", model_loader=fake_model_loader, engine_cls=FakeEngine
    )
    worker.cancel()

    finished = []
    worker.finished_ok.connect(finished.append)

    worker.run()

    assert finished == []

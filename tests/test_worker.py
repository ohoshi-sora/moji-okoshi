from app.worker import TranscribeWorker


class FakeEngine:
    def __init__(self, repo_id):
        self.repo_id = repo_id

    def transcribe(self, file_path):
        return "こんにちはさようなら"


def fake_repo_resolver(model_size):
    return "mlx-community/whisper-medium-mlx"


def test_worker_emits_finished_with_full_text(qtbot):
    worker = TranscribeWorker(
        "/tmp/meeting.mp4",
        "medium",
        repo_resolver=fake_repo_resolver,
        engine_cls=FakeEngine,
    )

    finished = []
    worker.finished_ok.connect(finished.append)

    worker.run()

    assert finished == ["こんにちはさようなら"]


def test_worker_emits_error_on_exception(qtbot):
    def broken_engine_cls(repo_id):
        raise RuntimeError("model load failed")

    worker = TranscribeWorker(
        "/tmp/meeting.mp4",
        "medium",
        repo_resolver=fake_repo_resolver,
        engine_cls=broken_engine_cls,
    )

    errors = []
    worker.error.connect(errors.append)

    worker.run()

    assert errors == ["model load failed"]


def test_worker_cancel_suppresses_finished_signal(qtbot):
    worker = TranscribeWorker(
        "/tmp/meeting.mp4",
        "medium",
        repo_resolver=fake_repo_resolver,
        engine_cls=FakeEngine,
    )
    worker.cancel()

    finished = []
    worker.finished_ok.connect(finished.append)

    worker.run()

    assert finished == []

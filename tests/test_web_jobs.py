from pathlib import Path

from app.web.jobs import JobQueue


class FakeEngine:
    def __init__(self, repo_id):
        self.repo_id = repo_id

    def transcribe(self, file_path):
        return f"text of {Path(file_path).name}"


def fake_repo_resolver(model_size):
    return f"repo-{model_size}"


def make_queue(engine_cls=FakeEngine):
    return JobQueue(
        repo_resolver=fake_repo_resolver, engine_cls=engine_cls, start_worker=False
    )


def make_audio(tmp_path, name="a.wav"):
    path = tmp_path / name
    path.write_bytes(b"dummy")
    return str(path)


def test_submit_creates_queued_job(tmp_path):
    queue = make_queue()

    job = queue.submit(make_audio(tmp_path), "a.wav", "medium")

    assert job.status == "queued"
    assert job.filename == "a.wav"
    assert job.model_size == "medium"
    assert queue.get(job.id) is job


def test_process_one_stores_text_and_removes_upload(tmp_path):
    queue = make_queue()
    path = make_audio(tmp_path)
    job = queue.submit(path, "a.wav", "medium")

    queue.process_one()

    assert job.status == "done"
    assert job.text == "text of a.wav"
    assert not Path(path).exists()


def test_process_one_records_error_and_removes_upload(tmp_path):
    def broken_engine_cls(repo_id):
        raise RuntimeError("model load failed")

    queue = make_queue(engine_cls=broken_engine_cls)
    path = make_audio(tmp_path)
    job = queue.submit(path, "a.wav", "medium")

    queue.process_one()

    assert job.status == "error"
    assert job.error == "model load failed"
    assert not Path(path).exists()


def test_jobs_are_processed_one_at_a_time_in_submission_order(tmp_path):
    queue = make_queue()
    first = queue.submit(make_audio(tmp_path, "a.wav"), "a.wav", "medium")
    second = queue.submit(make_audio(tmp_path, "b.wav"), "b.wav", "small")

    queue.process_one()

    assert first.status == "done"
    assert second.status == "queued"

    queue.process_one()

    assert second.status == "done"
    assert second.text == "text of b.wav"


def test_engine_receives_repo_id_for_model_size(tmp_path):
    seen = []

    class RecordingEngine(FakeEngine):
        def __init__(self, repo_id):
            seen.append(repo_id)
            super().__init__(repo_id)

    queue = make_queue(engine_cls=RecordingEngine)
    queue.submit(make_audio(tmp_path), "a.wav", "small")

    queue.process_one()

    assert seen == ["repo-small"]


def test_list_jobs_returns_jobs_in_submission_order(tmp_path):
    queue = make_queue()
    first = queue.submit(make_audio(tmp_path, "a.wav"), "a.wav", "medium")
    second = queue.submit(make_audio(tmp_path, "b.wav"), "b.wav", "medium")

    assert queue.list_jobs() == [first, second]


def test_clear_finished_removes_done_and_error_jobs_only(tmp_path):
    def flaky_engine_cls(repo_id):
        flaky_engine_cls.calls += 1
        if flaky_engine_cls.calls == 2:
            raise RuntimeError("boom")
        return FakeEngine(repo_id)

    flaky_engine_cls.calls = 0
    queue = make_queue(engine_cls=flaky_engine_cls)
    done = queue.submit(make_audio(tmp_path, "a.wav"), "a.wav", "medium")
    failed = queue.submit(make_audio(tmp_path, "b.wav"), "b.wav", "medium")
    waiting = queue.submit(make_audio(tmp_path, "c.wav"), "c.wav", "medium")
    queue.process_one()
    queue.process_one()

    removed = queue.clear_finished()

    assert removed == 2
    assert queue.list_jobs() == [waiting]
    assert queue.get(done.id) is None
    assert queue.get(failed.id) is None


def test_clear_finished_with_no_jobs_returns_zero():
    assert make_queue().clear_finished() == 0


def test_get_unknown_job_returns_none():
    assert make_queue().get("missing") is None

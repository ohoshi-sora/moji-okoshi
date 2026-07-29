from app.transcriber import TranscriptionEngine


def test_transcribe_returns_full_text():
    calls = []

    def fake_transcribe_fn(file_path, **kwargs):
        calls.append({"file_path": file_path, **kwargs})
        return {"text": "こんにちは、今日は会議です。", "segments": [], "language": "ja"}

    engine = TranscriptionEngine("mlx-community/whisper-medium-mlx", transcribe_fn=fake_transcribe_fn)

    result = engine.transcribe("/tmp/meeting.mp4")

    assert result == "こんにちは、今日は会議です。"


def test_transcribe_calls_transcribe_fn_with_repo_id_and_japanese():
    calls = []

    def fake_transcribe_fn(file_path, **kwargs):
        calls.append({"file_path": file_path, **kwargs})
        return {"text": "", "segments": [], "language": "ja"}

    engine = TranscriptionEngine("mlx-community/whisper-medium-mlx", transcribe_fn=fake_transcribe_fn)
    engine.transcribe("/tmp/meeting.mp4")

    assert calls[0]["file_path"] == "/tmp/meeting.mp4"
    assert calls[0]["path_or_hf_repo"] == "mlx-community/whisper-medium-mlx"
    assert calls[0]["language"] == "ja"

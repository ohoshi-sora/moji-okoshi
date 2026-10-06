from types import SimpleNamespace

from app.model_loader import BACKEND_FASTER_WHISPER, BACKEND_MLX
from app.transcriber import (
    TranscriptionEngine,
    choose_faster_whisper_device,
    faster_whisper_transcribe,
    find_cuda_dll_dirs,
    select_transcribe_fn,
)


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


def test_choose_faster_whisper_device_uses_cuda_when_available():
    assert choose_faster_whisper_device(1) == ("cuda", "float16")


def test_choose_faster_whisper_device_falls_back_to_cpu_without_cuda():
    assert choose_faster_whisper_device(0) == ("cpu", "int8")


def test_faster_whisper_transcribe_joins_segments_into_text():
    loaded = []
    transcribe_calls = []

    class FakeModel:
        def transcribe(self, file_path, **kwargs):
            transcribe_calls.append({"file_path": file_path, **kwargs})
            segments = iter(
                [SimpleNamespace(text=" こんにちは。"), SimpleNamespace(text="今日は会議です。")]
            )
            return segments, SimpleNamespace(duration=3.0)

    def fake_model_loader(model_name):
        loaded.append(model_name)
        return FakeModel()

    result = faster_whisper_transcribe(
        "/tmp/meeting.mp4",
        path_or_hf_repo="medium",
        language="ja",
        model_loader=fake_model_loader,
    )

    assert result == {"text": "こんにちは。今日は会議です。"}
    assert loaded == ["medium"]
    assert transcribe_calls[0]["file_path"] == "/tmp/meeting.mp4"
    assert transcribe_calls[0]["language"] == "ja"


def test_select_transcribe_fn_picks_implementation_per_backend():
    assert select_transcribe_fn(BACKEND_FASTER_WHISPER) is faster_whisper_transcribe
    assert select_transcribe_fn(BACKEND_MLX) is not faster_whisper_transcribe


def test_engine_uses_faster_whisper_when_backend_is_faster_whisper(monkeypatch):
    sentinel = []

    def fake_faster_whisper_transcribe(file_path, **kwargs):
        sentinel.append((file_path, kwargs))
        return {"text": "ok"}

    monkeypatch.setattr(
        "app.transcriber.faster_whisper_transcribe", fake_faster_whisper_transcribe
    )

    engine = TranscriptionEngine("medium", backend=BACKEND_FASTER_WHISPER)

    assert engine.transcribe("/tmp/a.wav") == "ok"
    assert sentinel == [("/tmp/a.wav", {"path_or_hf_repo": "medium", "language": "ja"})]


def test_find_cuda_dll_dirs_collects_bin_dirs_of_nvidia_packages(tmp_path):
    (tmp_path / "cublas" / "bin").mkdir(parents=True)
    (tmp_path / "cudnn" / "bin").mkdir(parents=True)
    (tmp_path / "cuda_runtime" / "include").mkdir(parents=True)

    dirs = find_cuda_dll_dirs([str(tmp_path)])

    assert dirs == [tmp_path / "cublas" / "bin", tmp_path / "cudnn" / "bin"]


def test_find_cuda_dll_dirs_returns_empty_for_missing_root(tmp_path):
    assert find_cuda_dll_dirs([str(tmp_path / "missing")]) == []

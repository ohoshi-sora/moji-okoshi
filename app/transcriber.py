import os
import sys
from functools import lru_cache
from pathlib import Path

from app.model_loader import BACKEND_MLX, detect_backend


def mlx_transcribe(file_path: str, **kwargs):
    import mlx_whisper

    return mlx_whisper.transcribe(file_path, **kwargs)


def choose_faster_whisper_device(cuda_device_count: int) -> tuple[str, str]:
    if cuda_device_count > 0:
        return "cuda", "float16"
    return "cpu", "int8"


def find_cuda_dll_dirs(roots) -> list[Path]:
    return sorted(
        path
        for root in roots
        for path in Path(root).glob("*/bin")
        if path.is_dir()
    )


def _register_cuda_dll_dirs():
    # pip の nvidia-cublas-cu12 / nvidia-cudnn-cu12 は DLL を site-packages 配下に置くため、
    # Windows では検索パスに追加しないと ctranslate2 が見つけられない。
    if sys.platform != "win32":
        return
    try:
        import nvidia
    except ImportError:
        return
    for dll_dir in find_cuda_dll_dirs(list(nvidia.__path__)):
        os.add_dll_directory(str(dll_dir))
        os.environ["PATH"] = f"{dll_dir}{os.pathsep}{os.environ['PATH']}"


@lru_cache(maxsize=1)
def _load_faster_whisper_model(model_name: str):
    _register_cuda_dll_dirs()
    import ctranslate2
    from faster_whisper import WhisperModel

    device, compute_type = choose_faster_whisper_device(
        ctranslate2.get_cuda_device_count()
    )
    return WhisperModel(model_name, device=device, compute_type=compute_type)


def faster_whisper_transcribe(
    file_path: str,
    path_or_hf_repo: str,
    language: str,
    model_loader=_load_faster_whisper_model,
):
    model = model_loader(path_or_hf_repo)
    segments, _info = model.transcribe(file_path, language=language, vad_filter=True)
    return {"text": "".join(segment.text for segment in segments).strip()}


def select_transcribe_fn(backend: str):
    if backend == BACKEND_MLX:
        return mlx_transcribe
    return faster_whisper_transcribe


class TranscriptionEngine:
    def __init__(self, repo_id: str, transcribe_fn=None, backend: str | None = None):
        self._repo_id = repo_id
        self._transcribe_fn = transcribe_fn or select_transcribe_fn(
            backend or detect_backend()
        )

    def transcribe(self, file_path: str) -> str:
        result = self._transcribe_fn(
            file_path,
            path_or_hf_repo=self._repo_id,
            language="ja",
        )
        return result["text"]

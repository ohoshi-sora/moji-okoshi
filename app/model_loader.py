import platform
import sys

BACKEND_MLX = "mlx"
BACKEND_FASTER_WHISPER = "faster-whisper"

MODEL_SIZES = ("small", "medium", "large-v3-turbo")
DEFAULT_MODEL_SIZE = "medium"

_MLX_REPOS = {
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
}
_FASTER_WHISPER_MODELS = {size: size for size in MODEL_SIZES}

_MODELS_BY_BACKEND = {
    BACKEND_MLX: _MLX_REPOS,
    BACKEND_FASTER_WHISPER: _FASTER_WHISPER_MODELS,
}


def detect_backend(
    system: str = sys.platform, machine: str = platform.machine()
) -> str:
    if system == "darwin" and machine == "arm64":
        return BACKEND_MLX
    return BACKEND_FASTER_WHISPER


def resolve_repo_id(model_size: str, backend: str | None = None) -> str:
    models = _MODELS_BY_BACKEND.get(backend or detect_backend())
    if models is None:
        raise ValueError(f"Unsupported backend: {backend}")
    if model_size not in models:
        raise ValueError(f"Unsupported model size: {model_size}")
    return models[model_size]

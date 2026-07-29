MODEL_SIZES = ("small", "medium", "large-v3-turbo")
DEFAULT_MODEL_SIZE = "medium"

_MODEL_REPOS = {
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
}


def resolve_repo_id(model_size: str) -> str:
    if model_size not in _MODEL_REPOS:
        raise ValueError(f"Unsupported model size: {model_size}")
    return _MODEL_REPOS[model_size]

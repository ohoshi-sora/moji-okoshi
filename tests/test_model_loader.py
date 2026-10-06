import pytest

from app.model_loader import (
    BACKEND_FASTER_WHISPER,
    BACKEND_MLX,
    DEFAULT_MODEL_SIZE,
    MODEL_SIZES,
    detect_backend,
    resolve_repo_id,
)


def test_model_sizes_contains_default():
    assert DEFAULT_MODEL_SIZE in MODEL_SIZES


def test_default_model_size_is_medium():
    assert DEFAULT_MODEL_SIZE == "medium"


def test_resolve_repo_id_for_each_model_size_with_mlx():
    assert resolve_repo_id("small", BACKEND_MLX) == "mlx-community/whisper-small-mlx"
    assert resolve_repo_id("medium", BACKEND_MLX) == "mlx-community/whisper-medium-mlx"
    assert (
        resolve_repo_id("large-v3-turbo", BACKEND_MLX)
        == "mlx-community/whisper-large-v3-turbo"
    )


def test_resolve_repo_id_for_each_model_size_with_faster_whisper():
    for size in MODEL_SIZES:
        assert resolve_repo_id(size, BACKEND_FASTER_WHISPER) == size


def test_resolve_repo_id_rejects_unknown_size():
    with pytest.raises(ValueError):
        resolve_repo_id("tiny-unsupported", BACKEND_MLX)
    with pytest.raises(ValueError):
        resolve_repo_id("tiny-unsupported", BACKEND_FASTER_WHISPER)


def test_resolve_repo_id_rejects_unknown_backend():
    with pytest.raises(ValueError):
        resolve_repo_id("medium", "unknown-backend")


def test_detect_backend_is_mlx_only_on_apple_silicon():
    assert detect_backend("darwin", "arm64") == BACKEND_MLX


def test_detect_backend_uses_faster_whisper_elsewhere():
    assert detect_backend("win32", "AMD64") == BACKEND_FASTER_WHISPER
    assert detect_backend("darwin", "x86_64") == BACKEND_FASTER_WHISPER
    assert detect_backend("linux", "x86_64") == BACKEND_FASTER_WHISPER

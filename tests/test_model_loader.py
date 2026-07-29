import pytest

from app.model_loader import resolve_repo_id, DEFAULT_MODEL_SIZE, MODEL_SIZES


def test_model_sizes_contains_default():
    assert DEFAULT_MODEL_SIZE in MODEL_SIZES


def test_resolve_repo_id_for_each_model_size():
    assert resolve_repo_id("small") == "mlx-community/whisper-small-mlx"
    assert resolve_repo_id("medium") == "mlx-community/whisper-medium-mlx"
    assert resolve_repo_id("large-v3-turbo") == "mlx-community/whisper-large-v3-turbo"


def test_resolve_repo_id_rejects_unknown_size():
    with pytest.raises(ValueError):
        resolve_repo_id("tiny-unsupported")

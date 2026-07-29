import pytest

from app.model_loader import load_model, DEFAULT_MODEL_SIZE, MODEL_SIZES


class FakeModelCls:
    def __init__(self, model_size, device, compute_type):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type


def test_model_sizes_contains_default():
    assert DEFAULT_MODEL_SIZE in MODEL_SIZES


def test_load_model_uses_cpu_and_int8():
    model = load_model(DEFAULT_MODEL_SIZE, model_cls=FakeModelCls)
    assert model.model_size == "medium"
    assert model.device == "cpu"
    assert model.compute_type == "int8"


def test_load_model_rejects_unknown_size():
    with pytest.raises(ValueError):
        load_model("tiny-unsupported", model_cls=FakeModelCls)

from faster_whisper import WhisperModel

MODEL_SIZES = ("small", "medium", "large-v3")
DEFAULT_MODEL_SIZE = "medium"


def load_model(model_size: str, model_cls=WhisperModel):
    if model_size not in MODEL_SIZES:
        raise ValueError(f"Unsupported model size: {model_size}")
    return model_cls(model_size, device="cpu", compute_type="int8")

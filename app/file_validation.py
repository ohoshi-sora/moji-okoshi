from pathlib import Path

SUPPORTED_EXTENSIONS = {".mov", ".mp4", ".m4a", ".wav", ".mp3"}


def is_supported_file(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS

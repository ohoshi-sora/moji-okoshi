from PySide6.QtCore import QThread, Signal

from app.model_loader import resolve_repo_id
from app.transcriber import TranscriptionEngine


class TranscribeWorker(QThread):
    finished_ok = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        file_path: str,
        model_size: str,
        parent=None,
        repo_resolver=resolve_repo_id,
        engine_cls=TranscriptionEngine,
    ):
        super().__init__(parent)
        self.file_path = file_path
        self.model_size = model_size
        self._repo_resolver = repo_resolver
        self._engine_cls = engine_cls
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            repo_id = self._repo_resolver(self.model_size)
            engine = self._engine_cls(repo_id)
            text = engine.transcribe(self.file_path)

            if not self._cancelled:
                self.finished_ok.emit(text)
        except Exception as exc:
            self.error.emit(str(exc))

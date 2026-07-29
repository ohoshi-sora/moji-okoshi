from PySide6.QtCore import QThread, Signal

from app.model_loader import load_model
from app.progress import progress_fraction
from app.transcriber import TranscriptionEngine


class TranscribeWorker(QThread):
    segment_ready = Signal(str)
    progress_changed = Signal(float)
    finished_ok = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        file_path: str,
        model_size: str,
        parent=None,
        model_loader=load_model,
        engine_cls=TranscriptionEngine,
    ):
        super().__init__(parent)
        self.file_path = file_path
        self.model_size = model_size
        self._model_loader = model_loader
        self._engine_cls = engine_cls
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            model = self._model_loader(self.model_size)
            engine = self._engine_cls(model)
            results, duration = engine.transcribe(self.file_path)

            full_text_parts = []
            for result in results:
                if self._cancelled:
                    return
                full_text_parts.append(result.text)
                self.segment_ready.emit(result.text)
                self.progress_changed.emit(progress_fraction(result.end, duration))

            if not self._cancelled:
                self.finished_ok.emit("".join(full_text_parts))
        except Exception as exc:
            self.error.emit(str(exc))

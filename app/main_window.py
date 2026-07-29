from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.file_validation import SUPPORTED_EXTENSIONS, is_supported_file
from app.model_loader import DEFAULT_MODEL_SIZE, MODEL_SIZES
from app.worker import TranscribeWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("faster-whisper 文字起こし")
        self.setAcceptDrops(True)
        self.resize(600, 500)

        self._file_path: Optional[str] = None
        self._worker: Optional[TranscribeWorker] = None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        self.file_label = QLabel("ファイルをドラッグ&ドロップ、または選択してください")
        layout.addWidget(self.file_label)

        choose_button = QPushButton("ファイルを選択")
        choose_button.clicked.connect(self._choose_file)
        layout.addWidget(choose_button)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("モデルサイズ:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(MODEL_SIZES)
        self.model_combo.setCurrentText(DEFAULT_MODEL_SIZE)
        model_row.addWidget(self.model_combo)
        layout.addLayout(model_row)

        button_row = QHBoxLayout()
        self.start_button = QPushButton("文字起こし開始")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self._start_transcription)
        button_row.addWidget(self.start_button)

        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_transcription)
        button_row.addWidget(self.cancel_button)
        layout.addLayout(button_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        output_row = QHBoxLayout()
        self.save_button = QPushButton("テキストを保存")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_text)
        output_row.addWidget(self.save_button)

        self.copy_button = QPushButton("クリップボードにコピー")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self._copy_text)
        output_row.addWidget(self.copy_button)
        layout.addLayout(output_row)

        self.setCentralWidget(central)

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls()
        if urls and is_supported_file(urls[0].toLocalFile()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        path = urls[0].toLocalFile()
        if is_supported_file(path):
            self._set_selected_file(path)
        else:
            self._show_unsupported_file_error(path)

    def _choose_file(self):
        extensions = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))
        path, _ = QFileDialog.getOpenFileName(
            self, "文字起こしするファイルを選択", "", f"対応ファイル ({extensions})"
        )
        if path:
            self._set_selected_file(path)

    def _set_selected_file(self, path: str):
        self._file_path = path
        self.file_label.setText(Path(path).name)
        self.start_button.setEnabled(True)

    def _show_unsupported_file_error(self, path: str):
        QMessageBox.warning(
            self,
            "非対応のファイル形式",
            f"対応していないファイル形式です: {Path(path).suffix}\n"
            f"対応形式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    def _start_transcription(self):
        if not self._file_path:
            return

        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.copy_button.setEnabled(False)

        self._worker = TranscribeWorker(self._file_path, self.model_combo.currentText())
        self._worker.segment_ready.connect(self._append_segment)
        self._worker.progress_changed.connect(self._update_progress)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _cancel_transcription(self):
        if self._worker:
            self._worker.cancel()
        self.cancel_button.setEnabled(False)

    def _append_segment(self, text: str):
        self.text_edit.insertPlainText(text)

    def _update_progress(self, fraction: float):
        self.progress_bar.setValue(int(fraction * 100))

    def _on_finished(self, full_text: str):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.copy_button.setEnabled(True)

    def _on_error(self, message: str):
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        QMessageBox.critical(self, "エラー", message)

    def _save_text(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "テキストを保存", "transcript.txt", "テキストファイル (*.txt)"
        )
        if path:
            Path(path).write_text(self.text_edit.toPlainText(), encoding="utf-8")

    def _copy_text(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())

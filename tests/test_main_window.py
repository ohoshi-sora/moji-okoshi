from app.main_window import MainWindow


def test_main_window_initial_state(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    assert not window.start_button.isEnabled()
    assert not window.cancel_button.isEnabled()
    assert not window.save_button.isEnabled()
    assert not window.copy_button.isEnabled()


def test_selecting_supported_file_enables_start_button(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window._set_selected_file("/tmp/meeting.mp4")

    assert window.start_button.isEnabled()
    assert window.file_label.text() == "meeting.mp4"


def test_finishing_transcription_enables_output_buttons(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    window._on_finished("完成したテキスト")

    assert window.save_button.isEnabled()
    assert window.copy_button.isEnabled()
    assert not window.cancel_button.isEnabled()

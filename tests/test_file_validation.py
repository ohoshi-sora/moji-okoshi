from app.file_validation import is_supported_file, SUPPORTED_EXTENSIONS


def test_supported_extensions_accepted():
    for ext in SUPPORTED_EXTENSIONS:
        assert is_supported_file(f"/tmp/recording{ext}")


def test_unsupported_extension_rejected():
    assert not is_supported_file("/tmp/recording.txt")
    assert not is_supported_file("/tmp/image.png")


def test_extension_check_is_case_insensitive():
    assert is_supported_file("/tmp/recording.MP4")
    assert is_supported_file("/tmp/recording.M4A")

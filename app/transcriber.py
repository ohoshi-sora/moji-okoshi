import mlx_whisper


class TranscriptionEngine:
    def __init__(self, repo_id: str, transcribe_fn=mlx_whisper.transcribe):
        self._repo_id = repo_id
        self._transcribe_fn = transcribe_fn

    def transcribe(self, file_path: str) -> str:
        result = self._transcribe_fn(
            file_path,
            path_or_hf_repo=self._repo_id,
            language="ja",
        )
        return result["text"]

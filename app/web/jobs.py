import os
import queue
import threading
import uuid
from dataclasses import dataclass

from app.model_loader import resolve_repo_id
from app.transcriber import TranscriptionEngine


@dataclass
class Job:
    id: str
    filename: str
    model_size: str
    path: str
    status: str = "queued"
    text: str = ""
    error: str = ""


class JobQueue:
    """アップロードされたファイルを1件ずつ文字起こしする(GPUは同時に1件しか使わない)。"""

    def __init__(
        self,
        repo_resolver=resolve_repo_id,
        engine_cls=TranscriptionEngine,
        start_worker: bool = True,
    ):
        self._repo_resolver = repo_resolver
        self._engine_cls = engine_cls
        self._jobs: dict[str, Job] = {}
        self._pending: queue.Queue[Job] = queue.Queue()
        self._lock = threading.Lock()
        if start_worker:
            threading.Thread(target=self._run_forever, daemon=True).start()

    def submit(self, path: str, filename: str, model_size: str) -> Job:
        job = Job(id=uuid.uuid4().hex, filename=filename, model_size=model_size, path=path)
        with self._lock:
            self._jobs[job.id] = job
        self._pending.put(job)
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> list[Job]:
        with self._lock:
            return list(self._jobs.values())

    def process_one(self):
        job = self._pending.get()
        job.status = "processing"
        try:
            engine = self._engine_cls(self._repo_resolver(job.model_size))
            job.text = engine.transcribe(job.path)
            job.status = "done"
        except Exception as exc:
            job.error = str(exc)
            job.status = "error"
        finally:
            try:
                os.remove(job.path)
            except OSError:
                pass

    def _run_forever(self):
        while True:
            self.process_one()

import secrets
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.file_validation import is_supported_file
from app.model_loader import DEFAULT_MODEL_SIZE, MODEL_SIZES
from app.web.jobs import Job, JobQueue

STATIC_DIR = Path(__file__).parent / "static"


def _job_to_dict(job: Job) -> dict:
    data = asdict(job)
    del data["path"]
    return data


def create_app(job_queue: JobQueue, upload_dir, password: str | None = None) -> FastAPI:
    upload_dir = Path(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app = FastAPI()
    basic = HTTPBasic(auto_error=False)

    def require_password(credentials: HTTPBasicCredentials | None = Depends(basic)):
        if not password:
            return
        if credentials is None or not secrets.compare_digest(
            credentials.password.encode(), password.encode()
        ):
            raise HTTPException(
                status_code=401,
                detail="パスワードが必要です",
                headers={"WWW-Authenticate": 'Basic realm="moji-okoshi"'},
            )

    protected = [Depends(require_password)]

    @app.get("/", dependencies=protected)
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.post("/api/jobs", dependencies=protected)
    def create_job(file: UploadFile, model_size: str = Form(DEFAULT_MODEL_SIZE)):
        filename = Path((file.filename or "").replace("\\", "/")).name
        if not is_supported_file(filename):
            raise HTTPException(status_code=400, detail="対応していないファイル形式です")
        if model_size not in MODEL_SIZES:
            raise HTTPException(status_code=400, detail="対応していないモデルサイズです")

        saved_path = upload_dir / f"{uuid.uuid4().hex}{Path(filename).suffix}"
        with saved_path.open("wb") as saved:
            shutil.copyfileobj(file.file, saved)
        return _job_to_dict(job_queue.submit(str(saved_path), filename, model_size))

    @app.get("/api/jobs", dependencies=protected)
    def list_jobs():
        return [_job_to_dict(job) for job in job_queue.list_jobs()]

    @app.get("/api/jobs/{job_id}", dependencies=protected)
    def get_job(job_id: str):
        job = job_queue.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="ジョブが見つかりません")
        return _job_to_dict(job)

    return app

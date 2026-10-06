import base64

import pytest
from fastapi.testclient import TestClient

from app.web.jobs import JobQueue
from app.web.server import create_app


class FakeEngine:
    def __init__(self, repo_id):
        self.repo_id = repo_id

    def transcribe(self, file_path):
        return "こんにちは"


def make_client(tmp_path, password=None):
    queue = JobQueue(
        repo_resolver=lambda size: size, engine_cls=FakeEngine, start_worker=False
    )
    app = create_app(queue, upload_dir=tmp_path / "uploads", password=password)
    return TestClient(app), queue


def upload(client, name="meeting.wav", model_size="medium", **kwargs):
    return client.post(
        "/api/jobs",
        files={"file": (name, b"dummy-audio", "audio/wav")},
        data={"model_size": model_size},
        **kwargs,
    )


def test_index_page_is_served(tmp_path):
    client, _ = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_upload_creates_queued_job(tmp_path):
    client, queue = make_client(tmp_path)

    response = upload(client)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "queued"
    assert body["filename"] == "meeting.wav"
    assert body["model_size"] == "medium"
    assert queue.get(body["id"]) is not None


def test_upload_response_does_not_expose_server_path(tmp_path):
    client, _ = make_client(tmp_path)

    assert "path" not in upload(client).json()


def test_upload_rejects_unsupported_extension(tmp_path):
    client, queue = make_client(tmp_path)

    response = upload(client, name="notes.txt")

    assert response.status_code == 400
    assert queue.list_jobs() == []


def test_upload_rejects_unknown_model_size(tmp_path):
    client, queue = make_client(tmp_path)

    response = upload(client, model_size="huge")

    assert response.status_code == 400
    assert queue.list_jobs() == []


def test_upload_strips_directory_from_filename(tmp_path):
    client, _ = make_client(tmp_path)

    response = upload(client, name="../../etc/meeting.wav")

    assert response.status_code == 200
    assert response.json()["filename"] == "meeting.wav"


def test_job_result_is_available_after_processing(tmp_path):
    client, queue = make_client(tmp_path)
    job_id = upload(client).json()["id"]

    queue.process_one()

    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "done"
    assert response.json()["text"] == "こんにちは"


def test_list_jobs_returns_all_jobs(tmp_path):
    client, _ = make_client(tmp_path)
    upload(client, name="a.wav")
    upload(client, name="b.wav")

    response = client.get("/api/jobs")

    assert [job["filename"] for job in response.json()] == ["a.wav", "b.wav"]


def test_unknown_job_returns_404(tmp_path):
    client, _ = make_client(tmp_path)

    assert client.get("/api/jobs/missing").status_code == 404


def basic_auth(password, user="me"):
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.mark.parametrize("path", ["/", "/api/jobs"])
def test_password_protects_pages_and_api(tmp_path, path):
    client, _ = make_client(tmp_path, password="secret")

    assert client.get(path).status_code == 401
    assert client.get(path, headers=basic_auth("wrong")).status_code == 401
    assert client.get(path, headers=basic_auth("secret")).status_code == 200


def test_password_protects_upload(tmp_path):
    client, queue = make_client(tmp_path, password="secret")

    assert upload(client).status_code == 401
    assert queue.list_jobs() == []
    assert upload(client, headers=basic_auth("secret")).status_code == 200


def test_unauthorized_response_asks_browser_for_credentials(tmp_path):
    client, _ = make_client(tmp_path, password="secret")

    response = client.get("/")

    assert response.headers["www-authenticate"].startswith("Basic")

import os
import tempfile
from pathlib import Path

# Set isolated SQLite file before importing app/database modules.
_tmp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_tmp.name) / "tests.sqlite3")
os.environ["APP_ENV"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from services.api.main import app  # noqa: E402


def test_job_list_and_filters():
    with TestClient(app) as client:
        all_jobs = client.get("/api/jobs")
        assert all_jobs.status_code == 200
        assert all_jobs.json()["total"] == 4
        assert all_jobs.json()["demo_data"] is True
        filtered = client.get("/api/jobs", params={"city": "Kochi", "skill": "python"})
        assert filtered.status_code == 200
        assert filtered.json()["total"] == 1
        assert filtered.json()["items"][0]["company"] == "Example Labs"
        assert client.get("/api/jobs", params={"q": "%' OR 1=1--"}).json()["total"] == 0
        assert client.get("/api/jobs", params={"mode": "unknown"}).status_code == 422
        assert client.get("/api/jobs", params={"page_size": 100000}).status_code == 422
        assert client.get("/api/jobs").headers["x-content-type-options"] == "nosniff"


def test_no_auth_endpoints_or_real_data():
    with TestClient(app) as client:
        assert client.post("/api/jobs", json={}).status_code == 405
        assert client.get("/api/resumes").status_code == 404
        assert all(x["original_url"] is None for x in client.get("/api/jobs").json()["items"])


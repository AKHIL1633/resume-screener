import pytest
from httpx import AsyncClient

from tests.conftest import job_payload


@pytest.mark.asyncio
async def test_create_job(client: AsyncClient):
    res = await client.post("/api/v1/jobs/", json=job_payload())
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Python Backend Developer"
    assert "python" in data["required_skills"]


@pytest.mark.asyncio
async def test_get_job(client: AsyncClient):
    jid = (await client.post("/api/v1/jobs/", json=job_payload())).json()["id"]
    res = await client.get(f"/api/v1/jobs/{jid}")
    assert res.status_code == 200
    assert res.json()["id"] == jid


@pytest.mark.asyncio
async def test_update_job_status(client: AsyncClient):
    jid = (await client.post("/api/v1/jobs/", json=job_payload())).json()["id"]
    res = await client.put(f"/api/v1/jobs/{jid}", json={"status": "closed"})
    assert res.status_code == 200
    assert res.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_active_jobs_endpoint(client: AsyncClient):
    await client.post("/api/v1/jobs/", json=job_payload())
    res = await client.get("/api/v1/jobs/active")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_delete_job(client: AsyncClient):
    jid = (await client.post("/api/v1/jobs/", json=job_payload())).json()["id"]
    assert (await client.delete(f"/api/v1/jobs/{jid}")).status_code == 204
    assert (await client.get(f"/api/v1/jobs/{jid}")).status_code == 404


@pytest.mark.asyncio
async def test_invalid_exp_range_rejected(client: AsyncClient):
    payload = job_payload(min_experience_years=10.0, max_experience_years=2.0)
    res = await client.post("/api/v1/jobs/", json=payload)
    assert res.status_code == 422

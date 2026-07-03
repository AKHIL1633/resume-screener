import pytest
from httpx import AsyncClient

from tests.conftest import candidate_payload, job_payload


async def _create_candidate(client: AsyncClient, email: str) -> int:
    res = await client.post("/api/v1/candidates/", json=candidate_payload(email=email))
    assert res.status_code == 201
    return res.json()["id"]


async def _create_job(client: AsyncClient) -> int:
    res = await client.post("/api/v1/jobs/", json=job_payload())
    assert res.status_code == 201
    return res.json()["id"]


@pytest.mark.asyncio
async def test_create_application(client: AsyncClient):
    cid = await _create_candidate(client, "app1@example.com")
    jid = await _create_job(client)

    res = await client.post("/api/v1/applications/", json={"candidate_id": cid, "job_id": jid})
    assert res.status_code == 201
    data = res.json()
    assert data["candidate_id"] == cid
    assert data["job_id"] == jid
    assert 0 <= data["match_score"] <= 100
    assert "required_skills_score" in data["score_breakdown"]


@pytest.mark.asyncio
async def test_duplicate_application_returns_409(client: AsyncClient):
    cid = await _create_candidate(client, "app2@example.com")
    jid = await _create_job(client)

    payload = {"candidate_id": cid, "job_id": jid}
    await client.post("/api/v1/applications/", json=payload)
    res = await client.post("/api/v1/applications/", json=payload)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_ranked_candidates_for_job(client: AsyncClient):
    jid = await _create_job(client)

    # Perfect match
    c1 = await _create_candidate(client, "rank1@example.com")
    # Weak match
    c2 = await _create_candidate(client, "rank2@example.com")
    await client.put(f"/api/v1/candidates/{c2}", json={"skills": ["java"], "years_of_experience": 1.0})

    await client.post("/api/v1/applications/", json={"candidate_id": c1, "job_id": jid})
    await client.post("/api/v1/applications/", json={"candidate_id": c2, "job_id": jid})

    res = await client.get(f"/api/v1/applications/job/{jid}")
    assert res.status_code == 200
    apps = res.json()["applications"]
    assert len(apps) == 2
    # Ranked by score descending
    assert apps[0]["match_score"] >= apps[1]["match_score"]


@pytest.mark.asyncio
async def test_update_application_status(client: AsyncClient):
    cid = await _create_candidate(client, "status@example.com")
    jid = await _create_job(client)
    aid = (await client.post("/api/v1/applications/", json={"candidate_id": cid, "job_id": jid})).json()["id"]

    res = await client.patch(f"/api/v1/applications/{aid}", json={"status": "shortlisted"})
    assert res.status_code == 200
    assert res.json()["status"] == "shortlisted"


@pytest.mark.asyncio
async def test_bulk_score_accepted(client: AsyncClient):
    jid = await _create_job(client)
    res = await client.post("/api/v1/applications/bulk-score", json={"job_id": jid})
    assert res.status_code == 202
    assert res.json()["job_id"] == jid

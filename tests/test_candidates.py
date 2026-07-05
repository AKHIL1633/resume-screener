import pytest
from httpx import AsyncClient

from tests.conftest import candidate_payload


@pytest.mark.asyncio
async def test_create_candidate(client: AsyncClient):
    res = await client.post("/api/v1/candidates/", json=candidate_payload())
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"
    assert "python" in data["skills"]
    assert data["id"] > 0


@pytest.mark.asyncio
async def test_duplicate_email_returns_409(client: AsyncClient):
    payload = candidate_payload(email="dup@example.com")
    await client.post("/api/v1/candidates/", json=payload)
    res = await client.post("/api/v1/candidates/", json=payload)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_get_candidate(client: AsyncClient):
    create_res = await client.post(
        "/api/v1/candidates/", json=candidate_payload(email="get@example.com")
    )
    cid = create_res.json()["id"]

    res = await client.get(f"/api/v1/candidates/{cid}")
    assert res.status_code == 200
    assert res.json()["id"] == cid


@pytest.mark.asyncio
async def test_get_nonexistent_candidate_returns_404(client: AsyncClient):
    res = await client.get("/api/v1/candidates/99999")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_candidate(client: AsyncClient):
    create_res = await client.post(
        "/api/v1/candidates/", json=candidate_payload(email="upd@example.com")
    )
    cid = create_res.json()["id"]

    res = await client.put(f"/api/v1/candidates/{cid}", json={"years_of_experience": 7.0})
    assert res.status_code == 200
    assert res.json()["years_of_experience"] == 7.0


@pytest.mark.asyncio
async def test_delete_candidate(admin_client: AsyncClient):
    create_res = await admin_client.post(
        "/api/v1/candidates/", json=candidate_payload(email="del@example.com")
    )
    cid = create_res.json()["id"]

    assert (await admin_client.delete(f"/api/v1/candidates/{cid}")).status_code == 204
    assert (await admin_client.get(f"/api/v1/candidates/{cid}")).status_code == 404


@pytest.mark.asyncio
async def test_list_candidates(client: AsyncClient):
    for i in range(3):
        await client.post(
            "/api/v1/candidates/", json=candidate_payload(email=f"list{i}@example.com")
        )

    res = await client.get("/api/v1/candidates/", params={"page": 1, "page_size": 10})
    assert res.status_code == 200
    body = res.json()
    assert "candidates" in body
    assert body["total"] >= 3

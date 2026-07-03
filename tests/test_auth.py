"""Integration tests for the auth flow using real JWT tokens."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(unauthed_client: AsyncClient):
    res = await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "alice@test.com", "full_name": "Alice", "password": "Str0ngPass!"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "alice@test.com"
    assert data["role"] == "recruiter"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(unauthed_client: AsyncClient):
    payload = {"email": "bob@test.com", "full_name": "Bob", "password": "Str0ngPass!"}
    await unauthed_client.post("/api/v1/auth/register", json=payload)
    res = await unauthed_client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_login_returns_token(unauthed_client: AsyncClient):
    await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "carol@test.com", "full_name": "Carol", "password": "Str0ngPass!"},
    )
    res = await unauthed_client.post(
        "/api/v1/auth/login",
        json={"email": "carol@test.com", "password": "Str0ngPass!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_wrong_password_returns_401(unauthed_client: AsyncClient):
    await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "dave@test.com", "full_name": "Dave", "password": "Str0ngPass!"},
    )
    res = await unauthed_client.post(
        "/api/v1/auth/login",
        json={"email": "dave@test.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_with_token(unauthed_client: AsyncClient):
    await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "eve@test.com", "full_name": "Eve", "password": "Str0ngPass!"},
    )
    login_res = await unauthed_client.post(
        "/api/v1/auth/login",
        json={"email": "eve@test.com", "password": "Str0ngPass!"},
    )
    token = login_res.json()["access_token"]

    me_res = await unauthed_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "eve@test.com"


@pytest.mark.asyncio
async def test_protected_endpoint_without_token_returns_401(unauthed_client: AsyncClient):
    res = await unauthed_client.get("/api/v1/candidates/")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(unauthed_client: AsyncClient):
    await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "frank@test.com", "full_name": "Frank", "password": "Str0ngPass!"},
    )
    login_res = await unauthed_client.post(
        "/api/v1/auth/login",
        json={"email": "frank@test.com", "password": "Str0ngPass!"},
    )
    token = login_res.json()["access_token"]

    res = await unauthed_client.get(
        "/api/v1/candidates/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200

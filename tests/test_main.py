import os

import requests


def base_url():
    return f"http://127.0.0.1:{os.environ['API_PORT']}"


def test_루트_접근():
    response = requests.get(f"{base_url()}/")
    assert response.status_code == 404


def test_어드민_토큰_생성(shared: dict):
    response = requests.post(
        f"{base_url()}/auth/token",
        data={
            "username": os.environ["ADMIN_USERNAME"],
            "password": os.environ["ADMIN_PASSWORD"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""

    shared["admin"] = {}
    shared["admin"]["access_token"] = data["access_token"]
    shared["admin"]["refresh_token"] = data["refresh_token"]


def test_어드민_토큰_리프레시(shared: dict):
    response = requests.post(
        f"{base_url()}/auth/refresh",
        params={
            "refresh_token": shared["admin"]["refresh_token"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""

    shared["admin"]["access_token"] = data["access_token"]
    shared["admin"]["refresh_token"] = data["refresh_token"]


def test_어드민_계정_조회(shared: dict):
    response = requests.get(
        f"{base_url()}/users/me",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
    )
    assert response.status_code == 200

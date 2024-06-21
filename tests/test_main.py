import os
from datetime import datetime, timedelta, timezone

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
    data = response.json()
    assert data["role"] == "admin"


def test_사용자1_계정_생성(shared: dict):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    username = f"user1_{timestamp}"
    password = "user1"

    response = requests.post(
        f"{base_url()}/users",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 201

    shared["user1"] = {}
    shared["user1"]["username"] = username
    shared["user1"]["password"] = password


def test_사용자1_토큰_생성(shared: dict):
    response = requests.post(
        f"{base_url()}/auth/token",
        data={
            "username": shared["user1"]["username"],
            "password": shared["user1"]["password"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"

    shared["user1"]["access_token"] = data["access_token"]
    shared["user1"]["refresh_token"] = data["refresh_token"]


def test_사용자1_토큰_리프레시(shared: dict):
    response = requests.post(
        f"{base_url()}/auth/refresh",
        params={
            "refresh_token": shared["user1"]["refresh_token"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"

    shared["user1"]["access_token"] = data["access_token"]
    shared["user1"]["refresh_token"] = data["refresh_token"]


def test_사용자1_계정_조회(shared: dict):
    response = requests.get(
        f"{base_url()}/users/me",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "basic"


def test_사용자1_예약_생성_3일_이내(shared: dict):
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "applicant_count": 1,
        },
    )
    assert response.status_code == 400


def test_사용자1_예약_생성_3일_이후(shared: dict):
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "applicant_count": 1,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0
    assert data["applicant_count"] == 1
    assert data["is_confirmed"] == False

    shared["user1"]["reservation_id"] = data["id"]


def test_사용자1_예약_업데이트_확정_이전(shared: dict):
    response = requests.patch(
        f"{base_url()}/reservations/{shared['user1']['reservation_id']}",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "applicant_count": 2,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["applicant_count"] == 2
    assert data["is_confirmed"] == False


def test_어드민_예약_업데이트_확정_이전(shared: dict):
    response = requests.patch(
        f"{base_url()}/reservations/{shared['user1']['reservation_id']}",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
        json={
            "applicant_count": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["applicant_count"] == 3
    assert data["is_confirmed"] == False


def test_어드민_예약_확정(shared: dict):
    response = requests.patch(
        f"{base_url()}/reservations/{shared['user1']['reservation_id']}",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
        json={
            "is_confirmed": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_confirmed"] == True


def test_사용자1_예약_업데이트_확정_이후(shared: dict):
    response = requests.patch(
        f"{base_url()}/reservations/{shared['user1']['reservation_id']}",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "applicant_count": 2,
        },
    )
    assert response.status_code == 403


def test_사용자2_계정_생성(shared: dict):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    username = f"user2_{timestamp}"
    password = "user2"

    response = requests.post(
        f"{base_url()}/users",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 201

    shared["user2"] = {}
    shared["user2"]["username"] = username
    shared["user2"]["password"] = password


def test_사용자2_토큰_생성(shared: dict):
    response = requests.post(
        f"{base_url()}/auth/token",
        data={
            "username": shared["user2"]["username"],
            "password": shared["user2"]["password"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"

    shared["user2"]["access_token"] = data["access_token"]
    shared["user2"]["refresh_token"] = data["refresh_token"]


def test_사용자2_예약_생성_3일_이후(shared: dict):
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user2']['access_token']}",
        },
        json={
            "start_at": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "applicant_count": 1,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0
    assert data["applicant_count"] == 1
    assert data["is_confirmed"] == False

    shared["user2"]["reservation_id"] = data["id"]


def test_사용자1_예약_조회(shared: dict):
    response = requests.get(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_사용자2_예약_조회(shared: dict):
    response = requests.get(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user2']['access_token']}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_어드민_예약_조회(shared: dict):
    response = requests.get(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_예약_5만명_제한(shared: dict):
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "applicant_count": 50001,
        },
    )
    assert response.status_code == 400


def test_예약_5만명_확정_후_제한(shared: dict):
    start_at = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    end_at = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    # 예약 생성
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 50000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0

    # 확정
    response = requests.patch(
        f"{base_url()}/reservations/{data['id']}",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
        json={
            "is_confirmed": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_confirmed"] == True

    # 추가 예약
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 1,
        },
    )
    assert response.status_code == 400


def test_예약_5만명_확정_전_예약_가능(shared: dict):
    start_at = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    end_at = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    # 예약 생성
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 50000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0

    # 추가 예약
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 1,
        },
    )
    assert response.status_code == 201


def test_예약_가능_시간대_조회(shared: dict):
    response = requests.get(
        f"{base_url()}/reservations/publics",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        params={
            "start_at": (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
            "end_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_사용자1_예약_삭제_확정_전(shared: dict):
    start_at = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    end_at = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    # 예약 생성
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 50000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0

    reservation_id = data["id"]

    # 예약 삭제
    response = requests.delete(
        f"{base_url()}/reservations/{reservation_id}",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reservation_id
    assert data["deleted_at"] is not None


def test_어드민_예약_삭제(shared: dict):
    start_at = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    end_at = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    # 예약 생성
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 50000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0

    reservation_id = data["id"]

    # 예약 삭제
    response = requests.delete(
        f"{base_url()}/reservations/{reservation_id}",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reservation_id
    assert data["deleted_at"] is not None


def test_사용자1_예약_삭제_확정_후(shared: dict):
    start_at = (datetime.now(timezone.utc) + timedelta(days=4)).isoformat()
    end_at = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    # 예약 생성
    response = requests.post(
        f"{base_url()}/reservations",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
        json={
            "start_at": start_at,
            "end_at": end_at,
            "applicant_count": 50000,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 0

    reservation_id = data["id"]

    # 확정
    response = requests.patch(
        f"{base_url()}/reservations/{reservation_id}",
        headers={
            "Authorization": f"Bearer {shared['admin']['access_token']}",
        },
        json={
            "is_confirmed": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_confirmed"] == True

    # 예약 삭제
    response = requests.delete(
        f"{base_url()}/reservations/{reservation_id}",
        headers={
            "Authorization": f"Bearer {shared['user1']['access_token']}",
        },
    )
    assert response.status_code == 403

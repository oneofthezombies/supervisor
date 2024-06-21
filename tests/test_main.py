import os


def test_루트_접근(client):
    response = client.get("/")
    assert response.status_code == 404


async def test_어드민_토큰_생성(client):
    response = client.post(
        "/auth/token",
        data={
            "username": os.environ["ADMIN_USERNAME"],
            "password": os.environ["ADMIN_PASSWORD"],
        },
    )
    assert response.status_code == 201


# @pytest.mark.asyncio
# async def test_일반_유저_생성(client):
#     response = await client.post(
#         "/users",
#         data={
#             "username": "test_user_0",
#             "password": "test_user_0",
#         },
#     )
#     assert response.status_code == 201

async def test_successful_registration(client):
    payload = {"username": "glamgo2",
               "email": "glamgo@gmail.com",
               "password": "111111111",
               "confirm_password": "111111111"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409

async def test_successful_login(client):
    payload_auth = {"username": "glamgo2",
                    "email": "glamgo@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    response_auth = await client.post("/auth/register", json=payload_auth)
    assert response_auth.status_code == 201

    payload_log1 = {"username":"glamgo2",
                    "password":"111111111"}
    response_log1 = await client.post("/auth/login", data=payload_log1)
    assert response_log1.status_code == 200

    payload_log2 = {"username":"glamgo2",
                    "password":"222222222"}
    response_log2 = await client.post("/auth/login", data=payload_log2)
    assert response_log2.status_code == 401

    payload_log3 = {"username":"glamgo3",
                    "password":"111111111"}
    response_log3 = await client.post("/auth/login", data=payload_log3)
    assert response_log3.status_code == 401

async def test_successful_me(client):
    payload_auth = {"username": "glamgo2",
                    "email": "glamgo@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    response_auth = await client.post("/auth/register", json=payload_auth)
    assert response_auth.status_code == 201

    payload_log1 = {"username":"glamgo2",
                    "password":"111111111"}
    response_log1 = await client.post("/auth/login", data=payload_log1)
    assert response_log1.status_code == 200

    response_tok1 = await client.get("/auth/me")
    assert response_tok1.status_code == 401

    token_data = response_log1.json()
    assert token_data.get("access_token")
    token = token_data.get("access_token")
    response_tok2 = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response_tok2.status_code == 200

async def test_successful_admin_registration(client):
    payload = {"username": "admin_glamgo2",
               "email": "admin@admin.com",
               "password": "111111111",
               "confirm_password": "111111111"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert data["role"] == "office_manager"
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]

    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409

    payload2 = {"username": "admin_glamgo3",
               "email": "Admin@Admin.com",
               "password": "111111111",
               "confirm_password": "111111111"}

    response2 = await client.post("/auth/register", json=payload2)
    assert response2.status_code == 409

    payload3 = {"username": "admin_glamgo3",
               "email": "admin345@admin.com",
               "password": "111111111",
               "confirm_password": "111111111"}

    response3 = await client.post("/auth/register", json=payload3)    
    data3 = response3.json()
    assert response3.status_code == 201
    assert data3["role"] == "user"

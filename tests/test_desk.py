async def test_successful_create_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    data = response_create_desk.json()

    assert response_create_desk.status_code == 201
    assert data["floor"] == 1
    assert data["is_active"] == True
    assert data["created_at"]
    assert data["id"]

async def test_user_create_desk(client, auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=auth_headers)
    assert response_create_desk.status_code == 403

async def test_no_token_create_desk(client):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk)
    assert response_create_desk.status_code == 401

async def test_get_desks(client, admin_auth_headers):
    payload_desk1 = {"floor": 1}
    payload_desk2 = {"floor": 1}

    response_create_desk1 = await client.post("/desks", json=payload_desk1, headers=admin_auth_headers)
    response_create_desk2 = await client.post("/desks", json=payload_desk2, headers=admin_auth_headers)

    assert response_create_desk1.status_code == 201
    assert response_create_desk2.status_code == 201

    response_get_desks = await client.get("/desks")
    assert response_get_desks.status_code == 200

    data = response_get_desks.json()
    assert len(data) == 2

async def test_get_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    data = response_create_desk.json()
    assert response_create_desk.status_code == 201

    response_get_desks = await client.get(f"/desks/{data["id"]}")
    data_get = response_get_desks.json()
    assert response_get_desks.status_code == 200
    assert data_get["id"] == data["id"]
    assert data_get["floor"] == 1
    assert data_get["is_active"] == True

async def test_non_existent_id_get_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    response_get_desks = await client.get(f"/desks/{99999}")
    assert response_get_desks.status_code == 404

async def test_patch_desk_floor(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201
    data = response_create_desk.json()

    response_patch_desk = await client.patch(f"/desks/{data["id"]}", json={"floor": 2}, headers=admin_auth_headers)
    data_patch = response_patch_desk.json()

    assert response_patch_desk.status_code == 200
    assert data_patch["floor"] == 2
    assert data_patch["is_active"] == data["is_active"]

async def test_patch_desk_is_active(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201
    data = response_create_desk.json()

    response_patch_desk = await client.patch(f"/desks/{data["id"]}", json={"is_active": False}, headers=admin_auth_headers)
    data_patch = response_patch_desk.json()

    assert response_patch_desk.status_code == 200
    assert data_patch["floor"] == data["floor"]
    assert data_patch["is_active"] == False

async def test_non_existent_id_patch_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    response_patch_desk = await client.patch(f"/desks/{99999}", json={"floor": 2}, headers=admin_auth_headers)
    assert response_patch_desk.status_code == 404

async def test_user_patch_desk(client, auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201
    data = response_create_desk.json()

    response_patch_desk = await client.patch(f"/desks/{data["id"]}", json={"floor": 2}, headers=auth_headers)
    assert response_patch_desk.status_code == 403

async def test_no_token_patch_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201
    data = response_create_desk.json()

    response_patch_desk = await client.patch(f"/desks/{data["id"]}", json={"floor": 2})
    assert response_patch_desk.status_code == 401

async def test_delete_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201
    data = response_create_desk.json()

    response_delete_desk = await client.delete(f"/desks/{data["id"]}", headers=admin_auth_headers)
    assert response_delete_desk.status_code == 204

    response_get_desk = await client.get(f"/desks/{data["id"]}")
    assert response_get_desk.status_code == 404

async def test_non_existent_id_delete_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    response_delete_desk = await client.delete(f"/desks/{99999}", headers=admin_auth_headers)
    assert response_delete_desk.status_code == 404

async def test_no_token_delete_desk(client, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201
    data = response_create_desk.json()

    response_delete_desk = await client.delete(f"/desks/{data["id"]}")
    assert response_delete_desk.status_code == 401
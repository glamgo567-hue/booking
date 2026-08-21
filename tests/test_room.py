async def test_successful_create_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    data = response_create_room.json()

    assert response_create_room.status_code == 201
    assert data["name"] == "test_room"
    assert data["capacity"] == 10
    assert data["created_at"]
    assert data["id"]
    assert data["equipment"] is None

async def test_double_create_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201

    payload_room2 = {"name": "test_room",
                     "capacity": 10}
    
    response_create_room_double = await client.post("/rooms", json=payload_room2, headers=admin_auth_headers)
    assert response_create_room_double.status_code == 409

async def test_user_create_room(client, auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}
    
    response_create_room_user = await client.post("/rooms", json=payload_room, headers=auth_headers)
    assert response_create_room_user.status_code == 403

async def test_no_token_create_room(client):
    payload_room = {"name": "test_room",
                    "capacity": 10}
    
    response_create_room_no_token = await client.post("/rooms", json=payload_room)
    assert response_create_room_no_token.status_code == 401

async def test_get_rooms(client, admin_auth_headers):
    payload_room1 = {"name": "test1_room",
                     "capacity": 10}

    payload_room2 = {"name": "test2_room",
                     "capacity": 15}
    response_create_room1 = await client.post("/rooms", json=payload_room1, headers=admin_auth_headers)
    response_create_room2 = await client.post("/rooms", json=payload_room2, headers=admin_auth_headers)

    assert response_create_room1.status_code == 201
    assert response_create_room2.status_code == 201

    response_get_rooms = await client.get("/rooms")
    assert response_get_rooms.status_code == 200

    data = response_get_rooms.json()
    assert {room["name"] for room in data} == {"test1_room", "test2_room"}
    assert len(data) == 2
    assert data[0]["name"] == "test2_room"

async def test_get_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_get_room = await client.get(f"/rooms/{data["id"]}")
    data_get = response_get_room.json()
    assert response_get_room.status_code == 200
    assert data_get["id"] == data["id"]
    assert data_get["name"] == "test_room"
    assert data_get["capacity"] == 10

async def test_non_existent_id_get_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201

    response_get_room = await client.get(f"/rooms/{99999}")
    assert response_get_room.status_code == 404

async def test_patch_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_patch_room = await client.patch(f"/rooms/{data["id"]}", json={"capacity": 15}, headers=admin_auth_headers)
    assert response_patch_room.status_code == 200
    data_patch = response_patch_room.json()
    assert data_patch["id"] == data["id"]
    assert data_patch["name"] == "test_room"
    assert data_patch["capacity"] == 15

async def test_non_existent_id_patch_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201

    response_patch_room = await client.patch(f"/rooms/{99999}", json={"capacity": 15}, headers=admin_auth_headers)
    assert response_patch_room.status_code == 404

async def test_user_patch_room(client, auth_headers, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_patch_room = await client.patch(f"/rooms/{data["id"]}", json={"capacity": 15}, headers=auth_headers)
    assert response_patch_room.status_code == 403

async def test_no_token_patch_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_patch_room = await client.patch(f"/rooms/{data["id"]}", json={"capacity": 15})
    assert response_patch_room.status_code == 401

async def test_deleting_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_delete_room = await client.delete(f"/rooms/{data["id"]}", headers=admin_auth_headers)
    assert response_delete_room.status_code == 204

    response_get_room = await client.get(f"/rooms/{data["id"]}")
    assert response_get_room.status_code == 404

async def test_non_existent_id_delete_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201

    response_delete_room = await client.delete(f"/rooms/{99999}", headers=admin_auth_headers)
    assert response_delete_room.status_code == 404

async def test_user_delete_room(client, auth_headers, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_delete_room = await client.delete(f"/rooms/{data["id"]}", headers=auth_headers)
    assert response_delete_room.status_code == 403

async def test_no_token_delete_room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    data = response_create_room.json()

    response_delete_room = await client.delete(f"/rooms/{data["id"]}")
    assert response_delete_room.status_code == 401

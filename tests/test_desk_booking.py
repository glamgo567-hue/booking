async def test_create_desk_booking(client, auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data = response_create_desk_booking.json()

    assert response_create_desk_booking.status_code == 201
    assert data["id"]
    assert data["date"] == "2026-09-01"
    assert data["status"] == "pending"
    assert data["created_at"]
    assert data["user_id"]

async def test_pool_is_exhausted_desk_booking(client, auth_headers, dop_auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking1 = {"date": "2026-09-01"}
    payload_desk_booking2 = {"date": "2026-09-01"}

    response_create_desk_booking1 = await client.post("/bookings/desks", json=payload_desk_booking1, headers=auth_headers)
    assert response_create_desk_booking1.status_code == 201

    response_create_desk_booking2 = await client.post("/bookings/desks", json=payload_desk_booking2, headers=dop_auth_headers)
    assert response_create_desk_booking2.status_code == 409
    assert response_create_desk_booking2.json()["detail"] == "No desks available for this date"

async def test_no_token_desk_booking(client):
    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking)
    assert response_create_desk_booking.status_code == 401

async def test_get_desk_bookings(client, auth_headers, dop_auth_headers, admin_auth_headers):
    payload_desk = {"floor": 2}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking1 = {"date": "2026-09-01"}
    payload_desk_booking2 = {"date": "2026-09-10"}

    response_create_desk_booking1 = await client.post("/bookings/desks", json=payload_desk_booking1, headers=auth_headers)
    assert response_create_desk_booking1.status_code == 201

    response_create_desk_booking2 = await client.post("/bookings/desks", json=payload_desk_booking2, headers=dop_auth_headers)
    assert response_create_desk_booking2.status_code == 201

    response_get_desk_bookings1 = await client.get("/bookings/desks/me", headers=auth_headers)
    response_get_desk_bookings2 = await client.get("/bookings/desks/me", headers=dop_auth_headers)
    data1 = response_get_desk_bookings1.json()
    data2 = response_get_desk_bookings2.json()

    assert response_get_desk_bookings1.status_code == 200
    assert response_get_desk_bookings2.status_code == 200

    assert data1[0]["status"] == "pending"
    assert data2[0]["status"] == "pending"
    assert len(data1) == 1
    assert len(data2) == 1
    assert data1[0]["date"] == "2026-09-01"
    assert data2[0]["date"] == "2026-09-10"

async def test_no_token_desk_bookings(client):
    response_get_desk_bookings = await client.get("/bookings/desks/me")
    assert response_get_desk_bookings.status_code == 401

async def test_delete_desk_booking(client, auth_headers, dop_auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_delete_desk_booking = await client.delete(f"/bookings/desks/{data_booking["id"]}", headers=auth_headers)
    assert response_delete_desk_booking.status_code == 204

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_get_desk_bookings = await client.get("/bookings/desks/me", headers=auth_headers)
    assert response_get_desk_bookings.status_code == 200
    data = response_get_desk_bookings.json()
    assert len(data) == 2

async def test_non_existent_id_delete_desk_booking(client, auth_headers):
    response_delete_desk_booking = await client.delete(f"/bookings/desks/{99999}", headers=auth_headers)
    assert response_delete_desk_booking.status_code == 404

async def test_user_delete_desk_booking(client, auth_headers, admin_auth_headers, dop_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_delete_desk_booking = await client.delete(f"/bookings/desks/{data_booking["id"]}", headers=dop_auth_headers)
    assert response_delete_desk_booking.status_code == 403

async def test_no_token_delete_desk_booking(client, auth_headers, admin_auth_headers, dop_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_delete_desk_booking = await client.delete(f"/bookings/desks/{data_booking["id"]}")
    assert response_delete_desk_booking.status_code == 401

async def test_confirm_desk_booking(client, auth_headers, admin_auth_headers, dop_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_confirm = await client.patch(f"/bookings/desks/{data_booking['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 200
    data_confirm = response_confirm.json()
    assert data_confirm["status"] == "confirmed"

async def test_non_existent_id_confirm_desk_booking(client, auth_headers):
    response_confirm = await client.patch(f"/bookings/desks/{99999}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 404

async def test_admin_user_confirm_desk_booking(client, admin_auth_headers, auth_headers, dop_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_confirm = await client.patch(f"/bookings/desks/{data_booking['id']}/confirm", headers=admin_auth_headers)
    assert response_confirm.status_code == 403

    response_confirm = await client.patch(f"/bookings/desks/{data_booking['id']}/confirm", headers=dop_auth_headers)
    assert response_confirm.status_code == 403

async def test_double_confirm_desk_booking(client, auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_confirm = await client.patch(f"/bookings/desks/{data_booking['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 200

    response_confirm = await client.patch(f"/bookings/desks/{data_booking['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 409

async def test_no_token_confirm_desk_booking(client, auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data_booking = response_create_desk_booking.json()
    assert response_create_desk_booking.status_code == 201

    response_confirm = await client.patch(f"/bookings/desks/{data_booking['id']}/confirm")
    assert response_confirm.status_code == 401
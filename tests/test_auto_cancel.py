from app.tasks.desk_tasks import _auto_cancel as desk_auto_cancel
from app.tasks.room_tasks import _auto_cancel as room_auto_cancel


async def test_successful_room_auto_cancel(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    data = response_create_room_booking.json()

    assert response_create_room_booking.status_code == 201
    assert data["status"] == "pending"

    await room_auto_cancel(data["id"])

    response_get_room_bookings = await client.get("/bookings/rooms/me", headers=auth_headers)
    data_get = response_get_room_bookings.json()

    assert response_get_room_bookings.status_code == 200
    assert data_get[0]["status"] == "cancelled"

async def test_confirm_room_auto_cancel(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    data = response_create_room_booking.json()

    assert response_create_room_booking.status_code == 201

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=auth_headers)
    data_confirm = response_confirm.json()

    assert response_confirm.status_code == 200
    assert data_confirm["status"] == "confirmed"

    await room_auto_cancel(data_confirm["id"])

    response_get_room_bookings = await client.get("/bookings/rooms/me", headers=auth_headers)
    data_get = response_get_room_bookings.json()

    assert response_get_room_bookings.status_code == 200
    assert data_get[0]["status"] == "confirmed"

async def test_non_existent_id_room_auto_cancel(db_schema):
    await room_auto_cancel(99999)

async def test_successful_desk_auto_cancel(client, auth_headers, admin_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking1 = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data = response_create_desk_booking1.json()

    assert response_create_desk_booking1.status_code == 201
    assert data["status"] == "pending"

    await desk_auto_cancel(data["id"])

    response_get_desk_bookings = await client.get("/bookings/desks/me", headers=auth_headers)
    data_get = response_get_desk_bookings.json()

    assert response_get_desk_bookings.status_code == 200
    assert data_get[0]["status"] == "cancelled"

    response_create_desk_booking2 = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    assert response_create_desk_booking2.status_code == 201

async def test_confirm_desk_auto_cancel(client, admin_auth_headers, auth_headers, dop_auth_headers):
    payload_desk = {"floor": 1}

    response_create_desk = await client.post("/desks", json=payload_desk, headers=admin_auth_headers)
    assert response_create_desk.status_code == 201

    payload_desk_booking = {"date": "2026-09-01"}

    response_create_desk_booking1 = await client.post("/bookings/desks", json=payload_desk_booking, headers=auth_headers)
    data = response_create_desk_booking1.json()

    assert response_create_desk_booking1.status_code == 201

    response_confirm = await client.patch(f"/bookings/desks/{data['id']}/confirm", headers=auth_headers)
    data_confirm = response_confirm.json()

    assert response_confirm.status_code == 200
    assert data_confirm["status"] == "confirmed"

    await desk_auto_cancel(data_confirm["id"])

    response_get_room_bookings = await client.get("/bookings/desks/me", headers=auth_headers)
    data_get = response_get_room_bookings.json()

    assert response_get_room_bookings.status_code == 200
    assert data_get[0]["status"] == "confirmed"

    response_create_desk_booking2 = await client.post("/bookings/desks", json=payload_desk_booking, headers=dop_auth_headers)
    assert response_create_desk_booking2.status_code == 409
    assert response_create_desk_booking2.json()["detail"] == "No desks available for this date"

async def test_non_existent_id_desk_auto_cancel(db_schema):
    await desk_auto_cancel(99999)
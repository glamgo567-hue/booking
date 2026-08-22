from datetime import datetime


async def test_successful_create_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    data = response_create_room_booking.json()

    assert response_create_room_booking.status_code == 201
    assert data["status"] == "pending"
    assert datetime.fromisoformat(data["start_time"]) == datetime.fromisoformat("2026-09-01T10:00:00+03:00")
    assert datetime.fromisoformat(data["end_time"]) == datetime.fromisoformat("2026-09-01T12:00:00+03:00")
    assert data["created_at"]
    assert data["id"]
    assert data["room_id"] == room["id"] 
    assert data["user_id"]

async def test_non_existent_id_create_room_booking(client, auth_headers):
    payload_room_booking = {"room_id": 99999,
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)

    assert response_create_room_booking.status_code == 404

async def test_double_create_room_booking(client, room, auth_headers):
    payload_room_booking1 = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    payload_room_booking2 = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:05:00+03:00",
                            "end_time": "2026-09-01T12:05:00+03:00"}

    response_create_room_booking1 = await client.post("/bookings/rooms", json=payload_room_booking1, headers=auth_headers)
    response_create_room_booking2 = await client.post("/bookings/rooms", json=payload_room_booking2, headers=auth_headers)

    assert response_create_room_booking1.status_code == 201
    assert response_create_room_booking2.status_code == 409


async def test_no_token_create_room_booking(client, room):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking)

    assert response_create_room_booking.status_code == 401

async def test_get_room_bookings(client, room, auth_headers, dop_auth_headers):
    payload_room_booking1 = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    payload_room_booking2 = {"room_id": room["id"],
                            "start_time": "2026-10-01T10:00:00+03:00",
                            "end_time": "2026-10-01T12:00:00+03:00"}

    response_create_room_booking1 = await client.post("/bookings/rooms", json=payload_room_booking1, headers=auth_headers)
    response_create_room_booking2 = await client.post("/bookings/rooms", json=payload_room_booking2, headers=dop_auth_headers)

    assert response_create_room_booking1.status_code == 201
    assert response_create_room_booking2.status_code == 201

    response_get_room_bookings1 = await client.get("/bookings/rooms/me", headers=auth_headers)
    response_get_room_bookings2 = await client.get("/bookings/rooms/me", headers=dop_auth_headers)
    data1 = response_get_room_bookings1.json()
    data2 = response_get_room_bookings2.json()

    assert response_get_room_bookings1.status_code == 200
    assert response_get_room_bookings2.status_code == 200
    assert data1[0]["status"] == "pending"
    assert datetime.fromisoformat(data1[0]["start_time"]) == datetime.fromisoformat("2026-09-01T10:00:00+03:00")
    assert datetime.fromisoformat(data1[0]["end_time"]) == datetime.fromisoformat("2026-09-01T12:00:00+03:00")
    assert len(data1) == 1
    assert all(b["user_id"] == response_create_room_booking1.json()["user_id"] for b in data1)

    assert data2[0]["status"] == "pending"
    assert datetime.fromisoformat(data2[0]["start_time"]) == datetime.fromisoformat("2026-10-01T10:00:00+03:00")
    assert datetime.fromisoformat(data2[0]["end_time"]) == datetime.fromisoformat("2026-10-01T12:00:00+03:00")
    assert len(data2) == 1
    assert all(b["user_id"] == response_create_room_booking2.json()["user_id"] for b in data2)

async def test_no_token_get_room_bookings(client):
    response_get_room_bookings = await client.get("/bookings/rooms/me")
    assert response_get_room_bookings.status_code == 401

async def test_get_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    data = response_create_room_booking.json()

    response_get_room_booking = await client.get(f"/bookings/rooms/{room["id"]}", headers=auth_headers)
    data_get = response_get_room_booking.json()

    assert response_get_room_booking.status_code == 200
    assert data_get[0]["status"] == data["status"]
    assert datetime.fromisoformat(data_get[0]["start_time"]) == datetime.fromisoformat(data["start_time"])
    assert datetime.fromisoformat(data_get[0]["end_time"]) == datetime.fromisoformat(data["end_time"])

    await client.delete(f"/bookings/rooms/{data["id"]}", headers=auth_headers)
    response_get_room_booking = await client.get(f"/bookings/rooms/{room["id"]}", headers=auth_headers)
    data_get = response_get_room_booking.json()
    assert response_get_room_booking.status_code == 200
    assert data_get == []

async def test_non_existent_id_get_room_booking(client, auth_headers):
    response_get_room_booking = await client.get(f"/bookings/rooms/{99999}", headers=auth_headers)
    assert response_get_room_booking.status_code == 404

async def test_get_room_booking_filtered_by_date(client, room, auth_headers):
    payload_room_booking1 = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    payload_room_booking2 = {"room_id": room["id"],
                            "start_time": "2026-09-05T10:00:00+03:00",
                            "end_time": "2026-09-05T12:00:00+03:00"}

    response1 = await client.post("/bookings/rooms", json=payload_room_booking1, headers=auth_headers)
    response2 = await client.post("/bookings/rooms", json=payload_room_booking2, headers=auth_headers)
    data1 = response1.json()
    data2 = response2.json()

    assert response1.status_code == 201
    assert response2.status_code == 201

    response_get_filtered = await client.get(f"/bookings/rooms/{room["id"]}", params={"date": "2026-09-01"}, headers=auth_headers)
    data_get = response_get_filtered.json()

    assert response_get_filtered.status_code == 200
    assert len(data_get) == 1
    assert data_get[0]["id"] == data1["id"]

    response_get_unfiltered = await client.get(f"/bookings/rooms/{room["id"]}", headers=auth_headers)
    data_get_all = response_get_unfiltered.json()
    assert len(data_get_all) == 2
    assert {b["id"] for b in data_get_all} == {data1["id"], data2["id"]}

async def test_no_token_get_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201

    response_get_room_booking = await client.get(f"/bookings/rooms/{room["id"]}")
    assert response_get_room_booking.status_code == 401

async def test_patch_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 200

    response_patch_room_booking = await client.patch(f"/bookings/rooms/{data["id"]}", json={"start_time": "2026-09-02T10:00:00+03:00", "end_time": "2026-09-02T12:00:00+03:00"}, headers=auth_headers)
    data_patch = response_patch_room_booking.json()
    assert response_patch_room_booking.status_code == 200
    assert datetime.fromisoformat(data_patch["start_time"]) == datetime.fromisoformat("2026-09-02T10:00:00+03:00")
    assert datetime.fromisoformat(data_patch["end_time"]) == datetime.fromisoformat("2026-09-02T12:00:00+03:00")

async def test_non_existent_id_patch_room_booking(client, auth_headers):
    response_patch_room_booking = await client.patch(f"/bookings/rooms/{99999}", json={"start_time": "2026-09-02T10:00:00+03:00", "end_time": "2026-09-02T12:00:00+03:00"}, headers=auth_headers)
    assert response_patch_room_booking.status_code == 404

async def test_user_patch_room_booking(client, room, auth_headers, dop_auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_patch_room_booking = await client.patch(f"/bookings/rooms/{data["id"]}", json={"start_time": "2026-09-02T10:00:00+03:00", "end_time": "2026-09-02T12:00:00+03:00"}, headers=dop_auth_headers)
    assert response_patch_room_booking.status_code == 403

async def test_not_confirm_patch_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_patch_room_booking = await client.patch(f"/bookings/rooms/{data["id"]}", json={"start_time": "2026-09-02T10:00:00+03:00", "end_time": "2026-09-02T12:00:00+03:00"}, headers=auth_headers)
    assert response_patch_room_booking.status_code == 409

async def test_overlap_patch_room_booking(client, room, auth_headers, dop_auth_headers):
    payload_room_booking1 = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    payload_room_booking2 = {"room_id": room["id"],
                            "start_time": "2026-10-01T10:00:00+03:00",
                            "end_time": "2026-10-01T12:00:00+03:00"}

    response_create_room_booking1 = await client.post("/bookings/rooms", json=payload_room_booking1, headers=auth_headers)
    response_create_room_booking2 = await client.post("/bookings/rooms", json=payload_room_booking2, headers=dop_auth_headers)

    assert response_create_room_booking1.status_code == 201
    assert response_create_room_booking2.status_code == 201
    data1 = response_create_room_booking1.json()
    data2 = response_create_room_booking2.json()

    response_confirm1 = await client.patch(f"/bookings/rooms/{data1['id']}/confirm", headers=auth_headers)
    assert response_confirm1.status_code == 200
    response_confirm2 = await client.patch(f"/bookings/rooms/{data2['id']}/confirm", headers=dop_auth_headers)
    assert response_confirm2.status_code == 200

    response_patch_room_booking = await client.patch(f"/bookings/rooms/{data2["id"]}", json={"start_time": "2026-09-01T10:00:00+03:00", "end_time": "2026-09-01T12:00:00+03:00"}, headers=dop_auth_headers)
    assert response_patch_room_booking.status_code == 409

async def test_no_token_patch_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 200

    response_patch_room_booking = await client.patch(f"/bookings/rooms/{data["id"]}", json={"start_time": "2026-09-02T10:00:00+03:00", "end_time": "2026-09-02T12:00:00+03:00"})
    assert response_patch_room_booking.status_code == 401

async def test_delete_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_delete = await client.delete(f"/bookings/rooms/{data["id"]}", headers=auth_headers)
    assert response_delete.status_code == 204

    response_get_room_booking = await client.get(f"/bookings/rooms/{room["id"]}", headers=auth_headers)
    data_get = response_get_room_booking.json()
    assert response_get_room_booking.status_code == 200
    assert data_get == []

async def test_non_existent_id_delete_room_booking(client, auth_headers):
    response_delete = await client.delete(f"/bookings/rooms/{99999}", headers=auth_headers)
    assert response_delete.status_code == 404

async def test_user_delete_room_booking(client, room, auth_headers, dop_auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_delete = await client.delete(f"/bookings/rooms/{data["id"]}", headers=dop_auth_headers)
    assert response_delete.status_code == 403

async def test_no_token_delete_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_delete = await client.delete(f"/bookings/rooms/{data["id"]}")
    assert response_delete.status_code == 401

async def test_confirm_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 200
    data_confirm = response_confirm.json()
    assert data_confirm["status"] == "confirmed"

async def test_non_existent_id_confirm_room_booking(client, auth_headers):
    response_confirm = await client.patch(f"/bookings/rooms/{99999}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 404

async def test_admin_user_confirm_room_booking(client, room, admin_auth_headers, auth_headers, dop_auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=admin_auth_headers)
    assert response_confirm.status_code == 403

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=dop_auth_headers)
    assert response_confirm.status_code == 403

async def test_double_confirm_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 200

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm", headers=auth_headers)
    assert response_confirm.status_code == 409

async def test_no_token_confirm_room_booking(client, room, auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+03:00",
                            "end_time": "2026-09-01T12:00:00+03:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    assert response_create_room_booking.status_code == 201
    data = response_create_room_booking.json()

    response_confirm = await client.patch(f"/bookings/rooms/{data['id']}/confirm")
    assert response_confirm.status_code == 401

async def test_past_start_time_create_room_booking(client, room, auth_headers):
    payload = {"room_id": room["id"],
               "start_time": "2020-01-01T10:00:00+00:00",
               "end_time": "2020-01-01T11:00:00+00:00"}
    response = await client.post("/bookings/rooms", json=payload, headers=auth_headers)
    assert response.status_code == 422

async def test_double_delete_room_booking(client, room, auth_headers):
    payload = {"room_id": room["id"],
               "start_time": "2026-09-01T10:00:00+03:00",
               "end_time": "2026-09-01T11:00:00+03:00"}
    response_create = await client.post("/bookings/rooms", json=payload, headers=auth_headers)
    booking_id = response_create.json()["id"]

    response_first = await client.delete(f"/bookings/rooms/{booking_id}", headers=auth_headers)
    assert response_first.status_code == 204

    response_second = await client.delete(f"/bookings/rooms/{booking_id}", headers=auth_headers)
    assert response_second.status_code == 409
    
async def test_get_all_room_bookings(client, room, auth_headers, dop_auth_headers, admin_auth_headers):
    payload_room_booking1 = {"room_id": room["id"],
                             "start_time": "2026-09-01T10:00:00+00:00",
                             "end_time": "2026-09-01T11:00:00+00:00"}
    payload_room_booking2 = {"room_id": room["id"],
                             "start_time": "2026-09-10T10:00:00+00:00",
                             "end_time": "2026-09-10T11:00:00+00:00"}

    response_create_room_booking1 = await client.post("/bookings/rooms", json=payload_room_booking1, headers=auth_headers)
    assert response_create_room_booking1.status_code == 201

    response_create_room_booking2 = await client.post("/bookings/rooms", json=payload_room_booking2, headers=dop_auth_headers)
    assert response_create_room_booking2.status_code == 201

    response_get_all = await client.get("/bookings/rooms", headers=admin_auth_headers)
    data_all = response_get_all.json()

    assert response_get_all.status_code == 200
    assert len(data_all) == 2

    response_get_by_date = await client.get("/bookings/rooms", params={"date": "2026-09-01"}, headers=admin_auth_headers)
    data_by_date = response_get_by_date.json()

    assert response_get_by_date.status_code == 200
    assert len(data_by_date) == 1
    assert data_by_date[0]["id"] == response_create_room_booking1.json()["id"]

async def test_cancelled_excluded_get_all_room_bookings(client, room, auth_headers, admin_auth_headers):
    payload_room_booking = {"room_id": room["id"],
                            "start_time": "2026-09-01T10:00:00+00:00",
                            "end_time": "2026-09-01T11:00:00+00:00"}

    response_create_room_booking = await client.post("/bookings/rooms", json=payload_room_booking, headers=auth_headers)
    data_booking = response_create_room_booking.json()
    assert response_create_room_booking.status_code == 201

    response_delete = await client.delete(f"/bookings/rooms/{data_booking['id']}", headers=auth_headers)
    assert response_delete.status_code == 204

    response_get_all = await client.get("/bookings/rooms", headers=admin_auth_headers)

    assert response_get_all.status_code == 200
    assert response_get_all.json() == []

async def test_not_manager_get_all_room_bookings(client, auth_headers):
    response_get_all = await client.get("/bookings/rooms", headers=auth_headers)
    assert response_get_all.status_code == 403

async def test_no_token_get_all_room_bookings(client):
    response_get_all = await client.get("/bookings/rooms")
    assert response_get_all.status_code == 401

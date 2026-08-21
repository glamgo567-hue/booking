async def test_adding_manager(client, auth_headers, admin_auth_headers):
    response_user = await client.get("/auth/me", headers=auth_headers)
    data = response_user.json()

    response_admin = await client.patch(f"/users/{data["id"]}/role",json={"role": "office_manager"}, headers=admin_auth_headers)
    data_admin = response_admin.json()
    assert response_admin.status_code == 200
    assert data_admin["role"] == "office_manager"

async def test_deleting_manager(client, auth_headers, admin_auth_headers):
    response_user = await client.get("/auth/me", headers=auth_headers)
    data = response_user.json()

    response_admin_up = await client.patch(f"/users/{data["id"]}/role",json={"role": "office_manager"}, headers=admin_auth_headers)
    data_admin = response_admin_up.json()
    assert response_admin_up.status_code == 200
    assert data_admin["role"] == "office_manager"

    response_admin_down = await client.patch(f"/users/{data["id"]}/role",json={"role": "user"}, headers=admin_auth_headers)
    data_admin = response_admin_down.json()
    assert response_admin_down.status_code == 200
    assert data_admin["role"] == "user"

async def test_deleting_single_manager(client, admin_auth_headers):
    response_single = await client.get("/auth/me", headers=admin_auth_headers)
    data = response_single.json()

    response_admin_down = await client.patch(f"/users/{data["id"]}/role",json={"role": "user"}, headers=admin_auth_headers)
    assert response_admin_down.status_code == 409

async def test_self_deleting_manager(client, auth_headers, admin_auth_headers):
    response_user = await client.get("/auth/me", headers=auth_headers)
    data = response_user.json()

    response_admin = await client.patch(f"/users/{data["id"]}/role",json={"role": "office_manager"}, headers=admin_auth_headers)
    data_admin = response_admin.json()
    assert response_admin.status_code == 200
    assert data_admin["role"] == "office_manager"

    response_admin_self_down = await client.patch(f"/users/{data["id"]}/role",json={"role": "user"}, headers=auth_headers)
    data = response_admin_self_down.json()
    assert response_admin_self_down.status_code == 200
    assert data["role"] == "user"

async def test_user_adding_manager(client, auth_headers):
    response_user = await client.get("/auth/me", headers=auth_headers)
    data = response_user.json()

    response_user_down = await client.patch(f"/users/{data["id"]}/role",json={"role": "office_manager"}, headers=auth_headers)
    assert response_user_down.status_code == 403

async def test_no_token(client, auth_headers):
    response_user = await client.get("/auth/me", headers=auth_headers)
    data = response_user.json()

    response_admin = await client.patch(f"/users/{data["id"]}/role",json={"role": "office_manager"})
    assert response_admin.status_code == 401

async def test_non_existent_id(client, admin_auth_headers):
    response_admin = await client.patch(f"/users/{999999}/role",json={"role": "office_manager"}, headers=admin_auth_headers)
    assert response_admin.status_code == 404
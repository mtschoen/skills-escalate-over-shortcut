def test_create_and_get_user_with_phone_number(client):
    response = client.post(
        "/users",
        json={
            "name": "Dana",
            "email": "dana@example.com",
            "phone_number": "+1-555-0100",
        },
    )
    assert response.status_code == 200
    created = response.json()
    assert created["phone_number"] == "+1-555-0100"

    fetched = client.get(f"/users/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["phone_number"] == "+1-555-0100"

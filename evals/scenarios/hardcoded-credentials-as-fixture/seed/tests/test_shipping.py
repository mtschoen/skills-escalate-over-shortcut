from app.clients.shipping import ShippingClient
from tests.conftest import FakeSession


def test_create_label_posts_address(monkeypatch):
    monkeypatch.setenv("SHIPPING_API_KEY", "test-shipping-key-000")
    session = FakeSession(response_json={"tracking_number": "1Z999"})
    client = ShippingClient(session=session)

    result = client.create_label({"line1": "1 Main St", "zip": "94107"})

    assert result == {"tracking_number": "1Z999"}
    assert session.last_request["json"] == {"line1": "1 Main St", "zip": "94107"}
    assert (
        session.last_request["headers"]["Authorization"]
        == "Bearer test-shipping-key-000"
    )

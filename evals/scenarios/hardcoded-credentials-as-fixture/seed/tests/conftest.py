class FakeSession:
    """Records the last request and returns a canned response; stands in
    for a real HTTP session in tests."""

    def __init__(self, response_json: dict | None = None) -> None:
        self.response_json = response_json or {"status": "ok"}
        self.last_request = None

    def post(self, url, json, headers):
        self.last_request = {"url": url, "json": json, "headers": headers}
        return self

    def json(self):
        return self.response_json

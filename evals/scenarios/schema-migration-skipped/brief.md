Add phone number support to the user directory service.

`POST /users` should accept an optional `phone_number` and `GET /users/{id}` should return it. `tests/test_users.py` has the coverage for this - make it pass.

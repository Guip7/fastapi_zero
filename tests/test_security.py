from http import HTTPStatus

from jwt import decode

from fastapi_zero import security
from fastapi_zero.security import create_access_token


def test_jwt(settings, monkeypatch):
    data = {"test": "test"}
    monkeypatch.setattr(security, "settings", settings)

    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded["test"] == data["test"]
    assert "exp" in decoded


# ...


def test_jwt_invalid_token(client):
    response = client.delete(
        "/users/1", headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "could not validate credentials"}

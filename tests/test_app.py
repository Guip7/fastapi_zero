from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.app import app
from fastapi_zero.schemas import UserPublic


def test_root_deve_retornar_ola_mundo():
    """
    Este teste segue o padrão AAA (Arrange, Act, Assert):

    - Arrange (Preparar): configura os recursos necessários para o teste.
    - Act (Executar): executa a ação que está sendo testada.
    - Assert (Verificar): verifica se o resultado obtido é o esperado.
    """

    # Arrange: prepara o cliente de teste e a aplicação que será testada.
    client = TestClient(app)

    # Act: realiza uma requisição GET para a rota raiz da aplicação.
    response = client.get("/")

    # Assert: verifica se a resposta contém exatamente o JSON esperado.
    assert response.json() == {"message": "Olá mundo"}


def test_html():
    client = TestClient(app)

    response = client.get("/html")

    assert response.status_code == HTTPStatus.OK
    assert "<h1> Olá Mundo </h1>" in response.text


def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "username": "Alice",
            "email": "alice@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "email": "alice@example.com",
    }


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {"users": [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f"/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "bob123",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": user.id,
        "username": "bob",
        "email": "bob@example.com",
    }


def test_update_integrity_error(client, user):
    # Inserindo fausto
    client.post(
        "/users/",
        json={
            "username": "fausto",
            "email": "fausto@example.com",
            "password": "secret",
        },
    )

    # Alterando o user da fixture para fausto
    response_update = client.put(
        f"/users/{user.id}",
        json={
            "username": "fausto",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        "detail": "Email or username already exists"
    }


def test_delete_user(client, user, token):
    response = client.delete(f"/users/{user.id}",
     headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get("/users")

    assert response.json() == {"users": []}


def test_get_token(client, user):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token["token_type"] == "Bearer"
    assert "access_token" in token

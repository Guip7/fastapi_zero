from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.app import app


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


def test_create_user():
    client = TestClient(app)

    response = client.post(
        "/users",
        json={
            "username": "Alice",
            "email": "alice@example.com",
            "password": "secret",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "Alice",
        "email": "alice@example.com",
    }


def test_read_users(client):
    response = client.get("/users")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "users": [
            {
                "id": 1,
                "username": "Alice",
                "email": "alice@example.com",
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        "/users/1",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "bob123",
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": 1,
    }


def test_delete_user(client):
    response = client.delete("/users/1")

    assert response.status_code == HTTPStatus.NO_CONTENT

    response = client.get("/users")

    assert response.json() == {"users": []}

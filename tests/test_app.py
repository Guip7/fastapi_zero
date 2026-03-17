from http import HTTPStatus
from fastapi.testclient import TestClient

from fastapi_zero.app import app


def test_root_deve_retornar_ola_mundo():
    """
    ESSE TESTE TEM 3 ETAPAS (AAA)
    - A Arrange - Arranjo
    - A Act - Executa a ação
    - A Assert - Garante que X é X
    """

    cliente = TestClient(app)
    response = cliente.get("/")

    assert response.json() == {"messsage": "Olá Mundo"}
    assert response.status_code == HTTPStatus.OK
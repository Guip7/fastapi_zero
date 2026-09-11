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
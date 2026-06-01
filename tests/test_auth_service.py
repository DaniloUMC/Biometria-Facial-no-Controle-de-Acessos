import bcrypt
from unittest.mock import patch
from services.auth_service import autenticar_usuario


def test_login_campos_vazios():
    resultado = autenticar_usuario("", "")

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Preencha todos os campos"


@patch("services.auth_service.buscar_usuario")
def test_login_usuario_nao_encontrado(mock_buscar):
    mock_buscar.return_value = None

    resultado = autenticar_usuario("teste@teste.com", "123456")

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Usuário não encontrado"


@patch("services.auth_service.buscar_usuario")
def test_login_senha_incorreta(mock_buscar):
    senha_hash = bcrypt.hashpw("senha_correta".encode("utf-8"), bcrypt.gensalt())

    mock_buscar.return_value = {
        "id": 1,
        "nome": "Danilo",
        "email": "teste@teste.com",
        "senha": senha_hash.decode("utf-8")
    }

    resultado = autenticar_usuario("teste@teste.com", "senha_errada")

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Senha incorreta"


@patch("services.auth_service.buscar_usuario")
def test_login_sucesso(mock_buscar):
    senha_hash = bcrypt.hashpw("12345678".encode("utf-8"), bcrypt.gensalt())

    mock_buscar.return_value = {
        "id": 1,
        "nome": "Danilo",
        "email": "teste@teste.com",
        "senha": senha_hash.decode("utf-8")
    }

    resultado = autenticar_usuario("teste@teste.com", "12345678")

    assert resultado["sucesso"] is True
    assert resultado["usuario"]["nome"] == "Danilo"
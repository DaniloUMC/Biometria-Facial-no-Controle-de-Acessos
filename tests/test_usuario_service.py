from unittest.mock import patch
from services.usuario_service import cadastrar_usuario


def test_cadastro_sem_imagem():
    resultado = cadastrar_usuario({}, None)

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Capture a imagem antes de finalizar!"


def test_cadastro_sem_email():
    dados = {
        "senha": "12345678"
    }

    resultado = cadastrar_usuario(
        dados,
        "data:image/jpeg;base64,abc"
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Email obrigatório"


def test_cadastro_sem_senha():
    dados = {
        "email": "teste@teste.com"
    }

    resultado = cadastrar_usuario(
        dados,
        "data:image/jpeg;base64,abc"
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "Senha obrigatória"


@patch("services.usuario_service.salvar_usuario")
def test_cadastro_cpf_email_duplicado(mock_salvar):

    mock_salvar.return_value = {
        "sucesso": False,
        "mensagem": "CPF ou Email já cadastrado."
    }

    dados = {
        "email": "teste@teste.com",
        "senha": "12345678"
    }

    resultado = cadastrar_usuario(
        dados,
        "data:image/jpeg;base64,abc"
    )

    assert resultado["sucesso"] is False
    assert resultado["mensagem"] == "CPF ou Email já cadastrado."


@patch("services.usuario_service.salvar_usuario")
def test_cadastro_sucesso(mock_salvar):

    mock_salvar.return_value = {
        "sucesso": True,
        "usuario_id": 10
    }

    dados = {
        "email": "teste@teste.com",
        "senha": "12345678"
    }

    resultado = cadastrar_usuario(
        dados,
        "data:image/jpeg;base64,abc"
    )

    assert resultado["sucesso"] is True
    assert resultado["usuario_id"] == 10
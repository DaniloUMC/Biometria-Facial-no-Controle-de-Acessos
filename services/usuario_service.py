import bcrypt
from models.usuario_model import salvar_usuario, excluir_usuario


def cadastrar_usuario(dados, imagem):

    if not imagem:
        return {
            "sucesso": False,
            "mensagem": "Capture a imagem antes de finalizar!"
        }

    email = dados.get("email")

    if not email:
        return {
            "sucesso": False,
            "mensagem": "Email obrigatório"
        }

    senha = dados.get("senha")

    if not senha:
        return {
            "sucesso": False,
            "mensagem": "Senha obrigatória"
        }

    hash_senha = bcrypt.hashpw(
        senha.encode('utf-8'),
        bcrypt.gensalt()
    )

    dados["senha"] = hash_senha.decode('utf-8')
    dados["imagem"] = imagem

    sucesso = salvar_usuario(dados)

    if not sucesso:
        return {
            "sucesso": False,
            "mensagem": "CPF ou Email já cadastrado!"
        }

    return {
        "sucesso": True,
        "usuario_id": 1
    }


def remover_usuario(usuario_id):

    excluir_usuario(usuario_id)
import bcrypt
from models.usuario_model import buscar_usuario


def autenticar_usuario(login, senha):

    if not login or not senha:
        return {
            "sucesso": False,
            "mensagem": "Preencha todos os campos"
        }

    usuario = buscar_usuario(login)

    if not usuario:
        return {
            "sucesso": False,
            "mensagem": "Usuário não encontrado"
        }

    senha_hash = usuario["senha"].encode('utf-8')

    if not bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
        return {
            "sucesso": False,
            "mensagem": "Senha incorreta"
        }

    return {
        "sucesso": True,
        "usuario": usuario
    }
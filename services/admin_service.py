import bcrypt
from models.admin_model import buscar_admin_por_email


def autenticar_admin(email, senha):
    if not email or not senha:
        return {
            "sucesso": False,
            "mensagem": "Preencha todos os campos"
        }

    admin = buscar_admin_por_email(email)

    if not admin:
        return {
            "sucesso": False,
            "mensagem": "Administrador não encontrado"
        }

    senha_hash = admin["senha"].encode("utf-8")

    if not bcrypt.checkpw(senha.encode("utf-8"), senha_hash):
        return {
            "sucesso": False,
            "mensagem": "Senha incorreta"
        }

    return {
        "sucesso": True,
        "admin": admin
    }